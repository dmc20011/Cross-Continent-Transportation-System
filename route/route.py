import heapq
import json
import mysql.connector
import os
import pika
import random
import time
from enum import Enum

DATE_FORMAT_STR = "%Y-%m-%d"

CONSOLIDATION_CHANNEL = 'Consolidation-Updates'
TRACKING_CHANNEL = 'Tracking-Updates'
SHIP_DB_HOST = os.environ.get("SHIP_DB_HOST", "shipmentdb")
SHIP_DB_NAME = os.environ.get("SHIP_DB_NAME", "shipmentdb")
ORDER_DB_HOST = os.environ.get("ORDER_DB_HOST", "orderdb")
ORDER_DB_NAME = os.environ.get("ORDER_DB_NAME", "orderdb")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "mypass")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")


# irl, transportation costs are generally inversely correlated to their delivery speed
# assume transportation mode costs as follows
#       sea, rail, truck, air
# cost: 2    3     4      10
#
# order's preferred mode will have cost=1
# standard orders will take path with least cost with tiebreakers: # of preferred, least hops, random
# express orders will take path with least hops with tiebreakers: # of preferred, highest cost (fastest), random

LOCATIONS = {
    "Toronto": 0,
    "Houston": 1,
    "Mumbai": 2,
    "Shanghai": 3,
    "Sydney": 4,
    "Rio de Janeiro": 5,
    "Cairo": 6,
    "Berlin": 7
}

BASE_COST = {
    "Sea": 2,
    "Rail": 3,
    "Truck": 4,
    "Air": 10
}


def edge_cost(mode, preferred_mode):
    if mode == preferred_mode:
        return 1
    return BASE_COST[mode]


def best_mode(modes, preferred_mode):
    best = None
    best_cost = float("inf")
    for m in modes:
        c = edge_cost(m, preferred_mode)
        if c < best_cost:
            best_cost = c
            best = m
    return best, best_cost


class Graph:
    def __init__(self):
        self.adj = {}

    def add_edge(self, u, v, modes):
        self.adj.setdefault(u, []).append((v, modes))
        self.adj.setdefault(v, []).append((u, modes))

    def neighbors(self, node):
        return self.adj.get(node, [])


def build_graph():
    g = Graph()
    edges = [
        (0, 1, "Air, Rail, Truck"),
        (0, 5, "Air"),
        (0, 7, "Air, Sea"),
        (1, 3, "Air"),
        (1, 5, "Air, Truck"),
        (1, 7, "Air"),
        (2, 3, "Air, Rail, Sea, Truck"),
        (2, 6, "Air, Sea"),
        (2, 7, "Air, Rail, Truck"),
        (4, 2, "Air, Sea"),
        (4, 3, "Air, Sea"),
        (4, 5, "Air, Sea"),
        (5, 6, "Air, Sea"),
        (6, 7, "Air, Sea"),
        (6, 4, "Air, Sea"),
    ]
    for u, v, m in edges:
        g.add_edge(u, v, [n.strip() for n in m.split(",")])
    return g


def find_route(graph, start, end, priority, preferred_mode):
    is_express = priority == "Express"
    metric = "hops" if is_express else "cost"
    pq = []
    heapq.heappush(pq, (0, start))
    states = {
        start: {
            "cost": 0,
            "hops": 0,
            "preferred": 0,
            "path": [start]
        }
    }
    while pq:
        _, node = heapq.heappop(pq)
        current = states[node]
        if node == end:
            return current
        for neighbor, modes in graph.neighbors(node):
            mode, cost = best_mode(modes, preferred_mode)
            candidate = {
                "cost": current["cost"] + cost,
                "hops": current["hops"] + 1,
                "preferred": current["preferred"] + (1 if mode == preferred_mode else 0),
                "path": current["path"] + [neighbor]
            }
            if neighbor not in states:
                states[neighbor] = candidate
                heapq.heappush(pq, (candidate[metric], neighbor))
            else:
                tiebreak = tiebreak_express(candidate, states[neighbor]) if is_express else tiebreak_standard(candidate, states[neighbor])
                if tiebreak:
                    states[neighbor] = candidate
                    heapq.heappush(pq, (candidate[metric], neighbor))
    return None


def tiebreak_standard(a, b):
    if a["cost"] != b["cost"]:
        return a["cost"] < b["cost"]
    if a["preferred"] != b["preferred"]:
        return a["preferred"] > b["preferred"]
    if a["hops"] != b["hops"]:
        return a["hops"] < b["hops"]
    return random.random() < 0.5


def tiebreak_express(a, b):
    if a["hops"] != b["hops"]:
        return a["hops"] < b["hops"]
    if a["preferred"] != b["preferred"]:
        return a["preferred"] > b["preferred"]
    if a["cost"] != b["cost"]:
        return a["cost"] > b["cost"]
    return random.random() < 0.5


class RouteService():
    def __init__(self):
        self.ship_db_conn = mysql.connector.connect(
            host=SHIP_DB_HOST,
            port=3306,
            user=DB_USER,
            password=DB_PASS,
            database=SHIP_DB_NAME
        )
        print(f"Connected to {SHIP_DB_HOST}")

        self.order_db_conn = mysql.connector.connect(
            host=ORDER_DB_HOST,
            port=3306,
            user=DB_USER,
            password=DB_PASS,
            database=ORDER_DB_NAME
        )
        print(f"Connected to {ORDER_DB_HOST}")

        self.mq_conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        print(f"Connected to {RABBITMQ_HOST}")

        mq_channel = self.mq_conn.channel()
        mq_channel.queue_declare(queue=CONSOLIDATION_CHANNEL)
        mq_channel.basic_consume(queue=CONSOLIDATION_CHANNEL, auto_ack=True, on_message_callback=self.on_new_consolidate)
        mq_channel.start_consuming()

    def on_new_consolidate(self, ch, method, properties, body):
        shipment = json.loads(body.decode())
        print(f"Received: {shipment}")

        src = LOCATIONS[shipment['origin']]
        dst = LOCATIONS[shipment['destination']]
        pri = shipment['priority']
        pre = shipment['transport_method']

        g = build_graph()
        route = find_route(g, src, dst, pri, pre)
        print(f"Found best route: {route}")

        with self.ship_db_conn.cursor() as cursor:
            route_query = "INSERT INTO routes (Route, DistKM) VALUES (%s, %s)"
            route_values = (json.dumps(route), 240)

            cursor.execute(route_query, route_values)
            self.ship_db_conn.commit()
            route_id = cursor.lastrowid

            shipment_query = "INSERT INTO shipments (Origin, Destination, TotalWeightKG, TotalVolumnM3, OrderIDs, Priority, PreferredTransportMode, OrderStatus, RouteID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            shipment_values = (
                (shipment["origin"],
                    shipment["destination"],
                    shipment["total_weight_kg"],
                    shipment["total_volume_m3"],
                    json.dumps(shipment["order_ids"]),
                    shipment.get("priority", "Standard"),
                    shipment.get("transport_method", "None"),
                    "Created",
                    route_id)
            )

            cursor.execute(shipment_query, shipment_values)
            self.ship_db_conn.commit()
            shipment_id = cursor.lastrowid
            print(f"Inserted shipment {shipment_id} with route {route_id}")

        with self.order_db_conn.cursor() as cursor:
            for order_id in shipment["order_ids"]:
                print(order_id)
                order_query = "SELECT * FROM orders WHERE ID = %s"
                order_values = (order_id,)

                cursor.execute(order_query, order_values)
                order = cursor.fetchone()

                class TransitMethod(Enum):
                    Sea = 1
                    Rail = 2
                    Truck = 3
                    Air = 4

                class OrderStatus(Enum):
                    Created = 1
                    Processing = 2 
                    Shipped = 3
                    Delivered = 4 
                    Cancelled = 5

                tracking = {
                    "username": order[2],
                    "orderNumber": str(order[0]),
                    "parentNumber": str(shipment_id),
                    "orderDate": order[1].strftime(DATE_FORMAT_STR), 
                    "currentLocation": shipment["origin"],
                    "targetLocation": shipment["destination"],
                    "distkm": 123,
                    "transporationMethod": TransitMethod[shipment.get("transport_method", "None")].value,
                    "orderStatus": OrderStatus["Created"].value
                }

                channel = self.mq_conn.channel()
                channel.queue_declare(queue=TRACKING_CHANNEL)
                channel.basic_publish("", routing_key=TRACKING_CHANNEL, body=json.dumps(tracking))
                print(f"Published tracking to {TRACKING_CHANNEL}: {tracking}")


if __name__ == "__main__":
    time.sleep(5)
    service = RouteService()

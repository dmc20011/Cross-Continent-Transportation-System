import heapq
import json
import mysql.connector
import os
import pika
import random
import time
from typing import List

CONSOLIDATION_CHANNEL = 'Consolidation-Updates'
DB_HOST = os.environ.get("DB_HOST", "shipmentdb")
DB_NAME = os.environ.get("DB_NAME", "shipmentdb")
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
        self.db_conn = mysql.connector.connect(
            host=DB_HOST,
            port=3306,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        print(f"Connected to {DB_HOST}")

        self.mq_conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        print(f"Connected to {RABBITMQ_HOST}")

        mq_channel = self.mq_conn.channel()
        mq_channel.queue_declare(queue=CONSOLIDATION_CHANNEL)
        mq_channel.basic_consume(queue=CONSOLIDATION_CHANNEL, auto_ack=True, on_message_callback=self.on_new_consolidate)
        mq_channel.start_consuming()

    def on_new_consolidate(self, ch, method, properties, body):
        data = json.loads(body.decode())
        print(f"Received: {data}")

        src = LOCATIONS[data['origin']]
        dst = LOCATIONS[data['destination']]
        pri = data['priority']
        pre = data['transport_method']

        g = build_graph()
        route = find_route(g, src, dst, pri, pre)
        print(route)

        # TODO: insert shipment and route into databse


if __name__ == "__main__":
    time.sleep(5)
    service = RouteService()

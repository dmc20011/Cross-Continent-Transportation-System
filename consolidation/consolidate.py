import os
import pika
import pymysql
import threading
import json
import requests
from fastapi import FastAPI, HTTPException

CONSOLIDATION_CHANNEL = 'Consolidation-Updates'
NEW_ORDER_CHANNEL = 'New-Order'

DB_HOST = os.environ.get("DB_HOST", "shipmentdb")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "mypass")
DB_NAME = os.environ.get("DB_NAME", "shipmentdb")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
MAX_WEIGHT_KG = int(os.environ.get("MAX_WEIGHT_KG", 1000))
MAX_VOLUME_M3 = int(os.environ.get("MAX_VOLUME_M3", 10))

VALID_CITIES = [
    "Toronto", "Houston", "Mumbai", "Shanghai", "Sydney", "Rio de Janeiro", "Cairo", "Berlin"
]

class PikaReceiver():
    def __init__(self, host, queue, callback):
        threading.Thread.__init__(self)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue)
        self.channel.basic_consume(queue, callback)
        self.thread = None

    def run(self):
        self.thread = threading.Thread(target=self.channel.start_consuming)
        self.thread.start()

    def stop(self):
        self.connection.add_callback_threadsafe(self.channel.stop_consuming)
        self.thread.join()


class ConsolidationService():
    def __init__(self):
        self.mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))

    def connect_to_db(self):
        self.connection = pymysql.connect(
            host=DB_HOST,
            port=3306,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )

    def init_db(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shipments (
                    id                        INT AUTO_INCREMENT PRIMARY KEY,
                    origin                    VARCHAR(255) NOT NULL,
                    destination               VARCHAR(255) NOT NULL,
                    total_weight_kg           DOUBLE NOT NULL,
                    total_volume_m3           DOUBLE NOT NULL,
                    order_ids                 JSON NOT NULL,
                    priority                  VARCHAR(50) DEFAULT 'standard',
                    transport_method          INT DEFAULT -1,
                    status                    VARCHAR(50) DEFAULT 'pending',
                    created                   DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        self.connection.commit()
        print("Database initialised.")

    def test_db(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM shipments")
            res = cursor.fetchall()
        for item in res:
            print(item)

    def connect_rabbitmq(self):
        channel = self.mq_connection.channel()
        channel.queue_declare(queue=CONSOLIDATION_CHANNEL)
        channel.queue_declare(queue=NEW_ORDER_CHANNEL)

        def on_new_order(ch, method, properties, body):
            print(f"New order received: {body}")

        self.receiver_thread = PikaReceiver(RABBITMQ_HOST, NEW_ORDER_CHANNEL, on_new_order)
        self.receiver_thread.run()

    def publish_shipment(self, shipment):
        try: # connection times out after a few mins for some reason, just reopen it
            self.mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        except:
            pass
        channel = self.mq_connection.channel()
        channel.queue_declare(queue=CONSOLIDATION_CHANNEL)
        channel.basic_publish("", routing_key=CONSOLIDATION_CHANNEL, body=json.dumps(shipment))
        print(f"Published shipment: {shipment}")

    def save_shipment(self, shipment):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO shipments
                   (origin, destination, total_weight_kg, total_volume_m3, order_ids, priority, transport_method)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (shipment["origin"], shipment["destination"],
                 shipment["total_weight_kg"], shipment["total_volume_m3"],
                 json.dumps(shipment["order_ids"]),
                 shipment.get("priority", "standard"),
                 shipment.get("transport_method", -1))
            )
        self.connection.commit()
        print(f"Inserted shipment: {shipment['order_ids']}")

    def consolidate(self, orders):
        for order in orders:
            if order["origin"] not in VALID_CITIES:
                raise ValueError(f"Invalid origin: {order['origin']}")
            if order["destination"] not in VALID_CITIES:
                raise ValueError(f"Invalid destination: {order['destination']}")

        groups = {}
        for order in orders: # Sort 'em
            key = (order["origin"], order["destination"], order["priority"], order["transport_method"])
            groups.setdefault(key, []).append(order)

        shipments = []
        for (origin, destination, priority, transport_method), group in groups.items():
            group.sort(key=lambda order: (order["pickup_deadline"], -order["item_weight"]))
            bins = []

            for order in group:
                volume = order["item_length"] * order["item_width"] * order["item_height"]
                weight = order["item_weight"]

                added = False
                for b in bins: # try to fit in an existing binn
                    if b["weight"] + weight <= MAX_WEIGHT_KG and b["volume"] + volume <= MAX_VOLUME_M3:
                        b["weight"] += weight
                        b["volume"] += volume
                        b["order_ids"].append(order["id"])
                        added = True
                        break

                if not added: # Otherwise get a new bin
                    bins.append({"weight": weight, "volume": volume, "order_ids": [order["id"]]})

            for b in bins:
                shipment = {
                    "origin": origin,
                    "destination": destination,
                    "total_weight_kg": b["weight"],
                    "total_volume_m3": b["volume"],
                    "order_ids": b["order_ids"],
                    "priority": priority,
                    "transport_method": transport_method
                }
                # self.save_shipment(shipment)
                self.publish_shipment(shipment)
                shipments.append(shipment)
        return shipments

# FastAPI endpoints
app = FastAPI()
service = ConsolidationService()

@app.on_event("startup")
def startup():
    service.connect_to_db()
    # service.init_db()
    service.connect_rabbitmq()

## Simple service life-check
@app.get("/health")
def health():
    return {"status": "ok"}

## Gets all consolidated shipments
@app.get("/shipments")
def get_shipments():
    with service.connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT * FROM shipments")
        return cursor.fetchall()

## Gets a shipment by id
@app.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: int):
    with service.connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT * FROM shipments WHERE id = %s", (shipment_id,))
        result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return result

## Updates the status of a shipment by id
@app.patch("/shipments/{shipment_id}/status")
def update_shipment(shipment_id: int, status: str):
    with service.connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("UPDATE shipments SET status = %s WHERE id = %s", (status, shipment_id))
    service.connection.commit()
    return {"id": shipment_id, "status": status}

## Manual consolidation trigger
@app.post("/consolidate")
def consolidate():
    orders = requests.get("http://orderservice:PORT/orders?status=pending").json()
    shipments = service.consolidate(orders)
    return {"shipments_created": len(shipments), "shipments": shipments}

@app.post("/test/publish")
def test():
    shipment = {
        "origin": "Toronto",
        "destination": "Cairo",
        "total_weight_kg": 34,
        "total_volume_m3": 1.2,
        "order_ids": [1001, 1002, 1003],
        "priority": "Standard",
        "transport_method": "Rail"
    }
    ConsolidationService.publish_shipment(service, shipment)

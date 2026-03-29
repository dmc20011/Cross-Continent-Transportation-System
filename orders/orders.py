# orders_api/main.py
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import mysql.connector
from datetime import datetime
import pika
import json
import os
import pymysql
import logging

DATE_FORMAT_STR = "%Y-%m-%d"

TRACKING_CHANNEL_CREATE_UPDATE = 'Tracking-Updates'
NEW_ORDER_CHANNEL = 'New-Order'

DB_HOST = os.environ.get("DB_HOST", "orderdb")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "mypass")
DB_NAME = os.environ.get("DB_NAME", "orderdb")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
app = FastAPI()
app = FastAPI()
origins = ["http://localhost:3000",
           "http://localhost:8000",
           "http://localhost:*",
           "https://localhost:8000/*",
           "https://localhost:3000/*", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Basic logging config
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

# app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["http://localhost:3000"],
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
# )


class OrderCreate(BaseModel):
    username: str
    originLocation: str
    destinationLocation: str
    itemLength: float
    itemWidth: float
    itemHeight: float
    itemWeight: float
    pickupDeadline: Optional[str] = None
    specialInstructions: Optional[str] = None
    transportMode: str
    priority: str


def get_db():
    #    return mysql.connector.connect(
    #        unix_socket="/opt/local/var/run/mariadb/mysqld.sock",
    #        user="root",
    #        password="root",
    #        database="transportation",
    #    )
    return pymysql.connect(
        host=DB_HOST,
        port=3306,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )


@app.post("/api/neworder")
def create_order(order: OrderCreate):
    logger.info("BEGIN create_order")
    try:
        logger.debug("Calling get_db()")
        conn = get_db()
        logger.debug("Got DB connection")
        cursor = conn.cursor()

        location_map = {
            "toronto": "Toronto",
            "houston": "Houston",
            "rio de janeiro": "Rio de Janeiro",
            "cairo": "Cairo",
            "berlin": "Berlin",
            "mumbai": "Mumbai",
            "shanghai": "Shanghai",
            "sydney": "Sydney"
        }
        transport_map = {
            "truck": "Truck",
            "air": "Air",
            "rail": "Rail",
            "ocean": "Sea",
        }
        priority_map = {
            "standard": "Standard",
            "express": "Express",
        }
        origin = location_map.get(order.originLocation, "Toronto")
        destination = location_map.get(order.destinationLocation, "Toronto")
        db_mode = transport_map.get(order.transportMode, "Truck")
        db_priority = priority_map.get(order.priority, "Standard")
        orderDate = datetime.now()
        dist_km = 0
        volume_m3 = order.itemLength * order.itemWidth * order.itemHeight

        sql = """
            INSERT INTO orders (
                created, username, origin, destination,
                weightkg, volumem3,
                priority, preferredtransportmode, status
            ) VALUES (
                NOW(), %s, %s, %s,
                %s, %s,
                %s, %s, %s
            )
        """

        print(f"Inserting {order}")

        logger.debug("Executing INSERT INTO orders")
        cursor.execute(
            sql,
            (
                order.username,
                origin,
                destination,
                order.itemWeight,
                volume_m3,
                db_priority,
                db_mode,
                "Created"
            ),
        )

        conn.commit()
        order_id = cursor.lastrowid
        logger.debug(f"Inserted order, order_id={order_id}")
        cursor.close()
        conn.close()

        # Send to tracking channel via RabbitMQ
        logger.debug("Connecting to RabbitMQ")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=TRACKING_CHANNEL_CREATE_UPDATE)

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

        order = {
            "username": order.username,
            "orderNumber": str(order_id),
            "parentNumber": '',
            "orderDate": orderDate.strftime("%Y-%m-%d"),
            "currentLocation": origin,
            "targetLocation": destination,
            "distkm": 0,
            "transporationMethod": TransitMethod[db_mode].value,  # [sic]
            "orderStatus": OrderStatus['Created'].value
        }

        print(f"Publishing to {TRACKING_CHANNEL_CREATE_UPDATE}: {order}")
        channel.basic_publish(
            exchange='',
            routing_key=TRACKING_CHANNEL_CREATE_UPDATE,
            body=json.dumps(order),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        # Notify consolidtion via rabbitmq
        logger.debug("Declaring NEW_ORDER_CHANNEL")
        # in case it doesn’t exist yet
        channel.queue_declare(queue=NEW_ORDER_CHANNEL)

        new_order_msg = {
            "event": "new order",
            "orderId": order_id,
        }

        print(f"Publishing to {NEW_ORDER_CHANNEL}: {new_order_msg}")
        channel.basic_publish(
            exchange='',
            routing_key=NEW_ORDER_CHANNEL,
            body=json.dumps(new_order_msg),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        connection.close()

        logger.debug("RabbitMQ publish done")

        logger.info("END create_order: success")

        return {"ok": True, "orderId": order_id}

    except Exception as e:
        print("Error in create_order:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders")
def get_order_data():
    try:
        logger.debug("Calling get_db()")
        print(f"getting all orders")
        orders = []
        conn = get_db()
        logger.debug("Got DB connection")
        cursor = conn.cursor()
        logger.debug("Executing SELECT * FROM orders")
        cursor.execute("SELECT * FROM orders")
        for item in cursor.fetchall():
            orders.append(item)

        logger.info("END get_order_data: success")
        return {"orders": orders}
    except Exception as e:
        print("Error in getting orders:", e)
        raise HTTPException(status_code=500, detail=str(e))

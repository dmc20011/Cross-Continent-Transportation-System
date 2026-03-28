# orders_api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pymysql
from datetime import datetime
import os
import pika
import json

TRACKING_CHANNEL_CREATE_UPDATE = 'Tracking-Updates'
NEW_ORDER_CHANNEL = 'New-Order'
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")

DB_HOST = os.environ.get("DB_HOST", "ordersdb")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "mypass")
DB_NAME = os.environ.get("DB_NAME", "ordersdb")

app = FastAPI()

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

def get_db(self):
    self.connection = pymysql.connect(
        host=DB_HOST,
        port=3306,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

@app.post("/api/orders")
def create_order(order: OrderCreate):
    try:
        conn = get_db()
        cursor = conn.cursor()

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
        transportMode = transport_map.get(order.transportMode, "Truck")
        priority = priority_map.get(order.priority, "Standard")

        dist_km = 0
        volume_m3 = order.itemLength * order.itemWidth * order.itemHeight

        sql = """
            INSERT INTO orders (
                created, origin, destination, dist_km,
                weight_kg, volume_m3, username,
                priority, preferred_transport_mode, status
            ) VALUES (
                NOW(), %s, %s, %s,
                %s, %s, %s,
                %s, %s, 'Created'
            )
        """

        cursor.execute(
            sql,
            (
                order.originLocation,
                order.destinationLocation,
                dist_km,
                order.itemWeight,
                volume_m3,
                order.username,
                priority,
                transportMode,
            ),
        )

        conn.commit()
        order_id = cursor.lastrowid
        cursor.close()
        conn.close()

        # Send to tracking via rabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=TRACKING_CHANNEL_CREATE_UPDATE, durable=True)

        order = {
            "username": order.username,
            "orderNumber": order_id,
            "parentNumber": 0,
            "orderDate": 0,
            "currentLocation": order.originLocation,
            "targetLocation": order.destinationLocation,
            "distkm": 0,
            "transporationMethod": transportMode,
            "orderStatus":"Created",
        }

        channel.basic_publish(
            exchange='',
            routing_key=TRACKING_CHANNEL_CREATE_UPDATE,
            body=json.dumps(order),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        # Send to consolidation via RabbitMQ
        channel.queue_declare(queue=NEW_ORDER_CHANNEL, durable=True)

        order = {
            "orderNumber": order_id,
            "origin": order.originLocation,
            "destination": order.destinationLocation,
            "volume": volume_m3,
            "weight": order.itemWeight,
            "transporationMethod": transportMode,
            "status":"Created",
        }

        channel.basic_publish(
            exchange='',
            routing_key=NEW_ORDER_CHANNEL,
            body=json.dumps(order),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        connection.close()

        return {"ok": True, "orderId": order_id}
    
    except Exception as e:
        print("Error in create_order:", e)
        raise HTTPException(status_code=500, detail=str(e))
# orders_api/main.py
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

TRACKING_CHANNEL_CREATE_UPDATE = 'Tracking-Updates'
NEW_ORDER_CHANNEL = 'New-Order'

DB_HOST = os.environ.get("DB_HOST", "ordersdb")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "mypass")
DB_NAME = os.environ.get("DB_NAME", "ordersdb")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
app = FastAPI()

#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["http://localhost:3000"],  
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
#)

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
#    return mysql.connector.connect(
#        unix_socket="/opt/local/var/run/mariadb/mysqld.sock",
#        user="root",
#        password="root",
#        database="transportation",
#    )
    self.connection = pymysql.connect(
            host=DB_HOST,
            port=3306,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
    )


@app.post("/api/neworder")
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
        db_mode = transport_map.get(order.transportMode, "Truck")
        db_priority = priority_map.get(order.priority, "Standard")
        orderDate = datetime.now()
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
                db_priority,
                db_mode,
            ),
        )

        conn.commit()
        order_id = cursor.lastrowid
        cursor.close()
        conn.close()

        # Send to tracking channel via RabbitMQ 
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=TRACKING_CHANNEL_CREATE_UPDATE, durable=True)

        order = {
            "username": order.username,
            "orderNumber": order_id,
            "parentNumber": '',
            "orderDate:": orderDate.strftime("%Y-%m-%d"),
            "currentLocation": order.originLocation,
            "targetLocation": order.destinationLocation,
            "diskm": 0,
            "transportationMethod": db_mode,
            "orderStatus": 'Created'
        }
        channel.basic_publish(
            exchange='',
            routing_key=TRACKING_CHANNEL_CREATE_UPDATE,
            body=json.dumps(order),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        # Notify consolidtion via rabbitmq
        channel.queue_declare(queue=NEW_ORDER_CHANNEL, durable=True)  # in case it doesn’t exist yet

        new_order_msg = {
            "event": "new order",
            "orderId": order_id,
        }

        channel.basic_publish(
            exchange='',
            routing_key=NEW_ORDER_CHANNEL,
            body=json.dumps(new_order_msg),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        connection.close()

        return {"ok": True, "orderId": order_id}
    
    except Exception as e:
        print("Error in create_order:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders")
def get_order_data():
    try:
        print(f"getting all orders")
        orders = []
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders")
        for item in cursor.fetchall():
            orders.append(item)

        return {"orders": orders}
    except Exception as e:
        print("Error in getting orders:", e)
        raise HTTPException(status_code=500, detail=str(e))


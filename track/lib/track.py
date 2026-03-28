import pika
import pymysql
import threading
import time
import numpy as np
from fastapi import FastAPI
import signal
import sys
from lib.req_bodies import *
from datetime import datetime, timedelta
import json
import os

TRACKING_CHANNEL_CREATE_UPDATE = 'Tracking-Updates'
TRACKING_CHANNEL_DELETE = 'Tracking-Delete'

SHIP_MAX_DIST_KM = 700
SHIP_MIN_DIST_KM = 500
TRAIN_MAX_DIST_KM = 900
TRAIN_MIN_DIST_KM = 720
TRUCK_MAX_DIST_KM = 860
TRUCK_MIN_DIST_KM = 840
PLANE_MAX_DIST_KM = 10000
PLANE_MIN_DIST_KM = 50


DATE_FORMAT_STR = "%Y-%m-%d"


class PikaReceiver():
    def __init__(self, host, queue, callback):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue)
        self.channel.basic_consume(queue, callback)
        self.thread = None

    def run(self):
        self.thread = threading.Thread(
            target=self.channel.start_consuming, daemon=True)
        self.thread.start()

    def stop(self):
        self.connection.add_callback_threadsafe(self.channel.stop_consuming)
        self.thread.join()


class TrackingService():
    def __init__(self, mq_host, db_host, db_user, db_pass, db_name):
        self.mq_connection_upsert = pika.BlockingConnection(
            pika.ConnectionParameters(host=mq_host,))
        self.mq_connection_delete = pika.BlockingConnection(
            pika.ConnectionParameters(host=mq_host))
        self.db_connection: pymysql.Connection = None
        self.connect_to_db(db_host, db_user, db_pass, db_name)

    def tracking_item_from_row(self, row):
        print(row)
        return TrackingItem(username=row[0],
                            orderNumber=row[1],
                            parentNumber=row[2],
                            orderDate=row[3].strftime(DATE_FORMAT_STR),
                            orderLastUpdate=row[4].strftime(DATE_FORMAT_STR),
                            startLocation=row[5],
                            currentLocation=row[6],
                            targetLocation=row[7],
                            distkm=row[8],
                            transportationMethod=TransitMethod[row[9]],
                            deliveryEstimateEarly=row[10].strftime(
                                DATE_FORMAT_STR),
                            deliveryEstimateLate=row[11].strftime(
                                DATE_FORMAT_STR),
                            orderStatus=OrderStatus[row[12]])

    def calculate_delivery_estimate(self, order_date: str, distance_km: int, transit_method: TransitMethod, first_track: bool):
        if first_track:
            min_days_to_deliver = 2
            max_days_to_deliver = 2
        else:
            min_days_to_deliver = 0
            max_days_to_deliver = 0
        max_dist = 0
        min_dist = 0
        if transit_method == TransitMethod.Sea:
            min_dist = SHIP_MIN_DIST_KM
            max_dist = SHIP_MAX_DIST_KM
        elif transit_method == TransitMethod.Rail:
            min_dist = TRAIN_MAX_DIST_KM
            max_dist = TRAIN_MIN_DIST_KM
        elif transit_method == TransitMethod.Truck:
            min_dist = TRUCK_MIN_DIST_KM
            max_dist = TRUCK_MAX_DIST_KM

        if transit_method == TransitMethod.Air and distance_km > 50:
            plane_dist = distance_km - PLANE_MIN_DIST_KM
            plane_days = np.round(plane_dist/PLANE_MAX_DIST_KM)
            # minimum 2 days for plane
            max_days_to_deliver += max(plane_days + 1, 2)
            # maybe same day shipping from plane to truck
            min_days_to_deliver = max_days_to_deliver - 1
        else:
            min_days_to_deliver += distance_km/max_dist
            max_days_to_deliver += distance_km/min_dist

        order_date = datetime.strptime(order_date, DATE_FORMAT_STR)
        early_delivery = (
            order_date + timedelta(days=min_days_to_deliver)).strftime(DATE_FORMAT_STR)
        late_delivery = (
            order_date + timedelta(days=max_days_to_deliver)).strftime(DATE_FORMAT_STR)
        return early_delivery, late_delivery

    def connect_to_db(self, host, user, pswd, db_name):
        self.db_connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=pswd,
            database=db_name
        )

    def check_for_user(self, username: str):
        print(f"checking for user: {username}")
        with self.db_connection.cursor() as cur:
            cur.execute("SELECT * FROM User WHERE username = %s", (username,))
            res = cur.fetchall()
            if len(res) > 0:
                return True
            else:
                return False

    def get_all_orders(self, username: str):
        print(f"getting orders for: {username}")
        tracking_items = []
        with self.db_connection.cursor() as cur:
            cur.execute(
                "SELECT * FROM Tracking WHERE username = %s", (username,))
            for item in cur.fetchall():
                tracking_items.append(self.tracking_item_from_row(item))
        return tracking_items

    def upsert_tracking_item(self, username: str, tracking_item: TrackingItem):
        with self.db_connection.cursor() as cur:
            cur.execute("""
                INSERT INTO Tracking (
                    username, orderNumber, parentNumber, orderDate, lastUpdate,
                    startLocation, currentLocation, targetLocation,
                    distKM, transportMethod, deliveryEstimateEarly,
                    deliveryEstimateLate, orderStatus
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    lastUpdate = VALUES(lastUpdate),
                    currentLocation = VALUES(currentLocation),
                    orderStatus = VALUES(orderStatus)
            """, (
                tracking_item.username,
                tracking_item.orderNumber,
                tracking_item.parentNumber,
                tracking_item.orderDate,
                tracking_item.orderLastUpdate,
                tracking_item.startLocation,
                tracking_item.currentLocation,
                tracking_item.targetLocation,
                tracking_item.distkm,
                tracking_item.transportationMethod.value,
                tracking_item.deliveryEstimateEarly,
                tracking_item.deliveryEstimateLate,
                tracking_item.orderStatus.value
            ))
            self.db_connection.commit()
            return True
        return False

    def create_tracking_item(self, tracking_data: CreateOrUpdateTracker):
        transit_method = TransitMethod(tracking_data.transporationMethod)

        early, late = self.calculate_delivery_estimate(tracking_data.orderDate,
                                                       tracking_data.distkm, transit_method, True)

        tracking_item = TrackingItem(username=tracking_data.username, orderNumber=tracking_data.orderNumber,
                                     parentNumber=tracking_data.parentNumber, orderDate=tracking_data.orderDate, orderLastUpdate=tracking_data.orderDate,
                                     startLocation=tracking_data.currentLocation, currentLocation=tracking_data.currentLocation,
                                     targetLocation=tracking_data.targetLocation, distkm=tracking_data.distkm,
                                     transportationMethod=transit_method, deliveryEstimateEarly=early, deliveryEstimateLate=late,
                                     orderStatus=tracking_data.orderStatus)

        return tracking_item

    # use old data to fill in any blanks

    def update_tracking_item(self, old_data: TrackingItem, tracking_data: CreateOrUpdateTracker):

        transit_method = TransitMethod(tracking_data.transporationMethod)
        order_update = datetime.now().strftime(DATE_FORMAT_STR)

        if transit_method.name != old_data.transportationMethod or tracking_data.distkm != old_data.distkm:
            early, late = self.calculate_delivery_estimate(tracking_data.orderDate,
                                                           tracking_data.distkm, transit_method, True)
        else:
            early = old_data.deliveryEstimateEarly
            late = old_data.deliveryEstimateLate

        tracking_item = TrackingItem(username=tracking_data.username, orderNumber=tracking_data.orderNumber,
                                     parentNumber=tracking_data.parentNumber, orderDate=old_data.orderDate, orderLastUpdate=order_update,
                                     startLocation=tracking_data.currentLocation, currentLocation=tracking_data.currentLocation,
                                     targetLocation=tracking_data.targetLocation, distkm=tracking_data.distkm,
                                     transportationMethod=transit_method, deliveryEstimateEarly=early, deliveryEstimateLate=late,
                                     orderStatus=tracking_data.orderStatus)

        return tracking_item

    def create_or_update_tracking_item(self, tracking_item: CreateOrUpdateTracker):
        with self.db_connection.cursor() as cur:
            cur.execute(
                "SELECT * FROM Tracking WHERE username = %s AND orderNumber = %s",
                (tracking_item.username, tracking_item.orderNumber)
            )
            row = cur.fetchone()

            if row:
                existing_instance = self.tracking_item_from_row(row)
                return self.update_tracking_item(existing_instance, tracking_item)
            else:
                return self.create_tracking_item(tracking_item)

    def add_user(self, username: str):
        print(f"Adding user: {username}")
        with self.db_connection.cursor() as cur:
            cur.execute("INSERT INTO User (username) VALUES (%s)", (username,))
            self.db_connection.commit()

    def delete_order(self, username: str, orderNumber: str):
        print(f"Deleting order: {orderNumber} from user: {username}")
        query = "DELETE FROM Tracking WHERE username = %s AND orderNumber = %s"
        with self.db_connection.cursor() as cur:
            cur.execute(query, (username, orderNumber))
            self.db_connection.commit()

    def delete_user(self, username):
        print(f"Deleting user: {username}")
        query = "DELETE FROM User WHERE username = %s"
        with self.db_connection.cursor() as cur:
            cur.execute(query, (username,))
            self.db_connection.commit()

    def connect_rabbitmq(self):
        channel = self.mq_connection_upsert.channel()
        channel.queue_purge(TRACKING_CHANNEL_CREATE_UPDATE)
        channel.queue_declare(TRACKING_CHANNEL_CREATE_UPDATE, durable=False)

        def create_update_cb(ch, method, properties, body):
            print("Got an update req")
            data = json.loads(body.decode())
            body = CreateOrUpdateTracker(**data)
            if type(body) == CreateOrUpdateTracker:
                print("create or update runs")
                if not service.check_for_user(body.username):
                    service.add_user(body.username)
                    time.sleep(0.01)
                new_tracking_item = self.create_or_update_tracking_item(tracking_item=body)
                self.upsert_tracking_item(new_tracking_item.username, new_tracking_item)
            else:
                print("Error in Upsert thread: bad request")

        channel_del = self.mq_connection_delete.channel()
        channel_del.queue_purge(TRACKING_CHANNEL_DELETE)
        channel_del.queue_declare(TRACKING_CHANNEL_DELETE, durable=False)

        def delete_cb(ch, method, properties, body):
            print("Got a delete req")
            data = json.loads(body.decode())

            if "orderNumber" in data.keys():
                self.delete_order(data["username"], data["orderNumber"])
            elif "username" in data.keys():
                self.delete_user(data["username"])
            else:
                print("Error in Deletion thread: bad request")

        self.upsert_thread = PikaReceiver(
            "localhost", TRACKING_CHANNEL_CREATE_UPDATE, create_update_cb)
        self.delete_thread = PikaReceiver(
            "localhost", TRACKING_CHANNEL_DELETE, delete_cb)
        self.upsert_thread.run()
        self.delete_thread.run()


service = TrackingService(os.getenv("RABBITMQ_HOST"), os.getenv("DB_HOST"), os.getenv("DB_USER"), os.getenv("DB_PASS"), os.getenv("DB_NAME"))

def lifespan(app: FastAPI, service: TrackingService = service):
    service.connect_rabbitmq()
    yield  # do then wait for execution, then finish when done
    service.upsert_thread.stop()
    service.delete_thread.stop()
    service.mq_connection_delete.close()
    service.mq_connection_upsert.close()
    service.db_connection.close()
    print("shutdown")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def default():
    print("hoi")


@app.get("/tracking/{user}")
def get_order_tracking_data(user):   # remove async
    if not service.check_for_user(user):
        service.add_user(user)
    orders = service.get_all_orders(user)
    if len(orders) > 0:
        return {"orders": orders}
    else:
        return Failure(fail="No orders found for user")

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
    def __init__(self, host, queue,callback):
        threading.Thread.__init__(self)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue)
        self.channel.basic_consume(queue,callback)
        self.thread = None

    def run(self):
        self.thread = threading.Thread(target=self.channel.start_consuming)
        self.thread.start()

    def stop(self):
        self.connection.add_callback_threadsafe(self.channel.stop_consuming)
        self.thread.join()



class TrackingService():
    def __init__(self, mq_host, db_host, db_user, db_pass):
        self.mq_connection_upsert = pika.BlockingConnection(pika.ConnectionParameters(host=mq_host))
        self.mq_connection_delete = pika.BlockingConnection(pika.ConnectionParameters(host=mq_host))
        self.db_connection: pymysql.Connection = None
        self.connect_to_db(db_host, db_user, db_pass)
        

    def tracking_item_from_row(self, row):
        return TrackingItem(orderNumber=row[1], parentNumber=row[2],
                    orderDate=row[3], orderLastUpdate=row[4],currentLocation=row[5],targetLocation=row[6],
                    transportationMethod=row[7], deliveryEstimateEarly=row[8], deliveryEstimateLate=row[9])

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
            max_days_to_deliver += max(plane_days + 1, 2) #minimum 2 days for plane
            min_days_to_deliver = max_days_to_deliver - 1 #maybe same day shipping from plane to truck
        else: 
            min_days_to_deliver += distance_km/max_dist
            max_days_to_deliver += distance_km/min_dist

        order_date = datetime.strptime(order_date, DATE_FORMAT_STR)
        early_delivery = (order_date + timedelta(days=min_days_to_deliver)).strftime(DATE_FORMAT_STR)
        late_delivery = (order_date + timedelta(days=max_days_to_deliver)).strftime(DATE_FORMAT_STR)
        return early_delivery, late_delivery


    def connect_to_db(self, host, user, pswd):
        self.db_connection = pymysql.connect(
            host=host,
            port = 3306,
            user=user,
            password=pswd,
            database="trackingdb"
        )

    def check_for_user(self, username: str):
        with self.db_connection.cursor() as cur:
            cur.execute(f"SELECT * FROM User WHERE username = '{username}'")
            res = cur.fetchall()
            if len(res) > 0:
                return True
            else:
                return False

    def get_all_orders(self, username: str):
        tracking_items = []
        with self.db_connection.cursor() as cur: 
            cur.execute(f"SELECT * FROM Tracking WHERE username = '{username}")
            for item in cur.fetchall():
                tracking_items.append(self.tracking_item_from_row(item))
            return tracking_items

    def upsert_tracking_item(self, username: str, tracking_item: TrackingItem):
        with self.db_connection.cursor() as cur:
            cur.execute(f"REPLACE INTO Tracking (username, orderNumber, parentNumber, orderDate, lastUpdate, startLocation, currentLocation, targetLocaiton, \
                    distKM, transportMethod, deliveryEstimateEarly, deliveryEstimateLate, orderStatus) VALUES \
                        ({tracking_item.username}, {tracking_item.orderNumber}, {tracking_item.parentNumber}, {tracking_item.orderDate},\
                        {tracking_item.orderLastUpdate}, {tracking_item.startLocation}, {tracking_item.currentLocation}, \
                        {tracking_item.targetLocation}, {tracking_item.distkm}, {tracking_item.transportationMethod}, \
                        {tracking_item.deliveryEstimateEarly}, {tracking_item.deliveryEstimateLate}, {tracking_item.orderStatus})", )
            self.db_connection.commit()
            return True
        return False
    
    def create_tracking_item(self, tracking_data: CreateOrUpdateTracker):
        transit_method = TransitMethod(tracking_data.transporationMethod)

        early,late = self.calculate_delivery_estimate(tracking_data.orderDate,
                        tracking_data.distkm, transit_method, True)
        
        tracking_item = TrackingItem(username=tracking_data.username, orderNumber=tracking_data.orderNumber, 
                                    parentNumber=tracking_data.parentNumber, orderDate=tracking_data.orderDate, orderLastUpdate=tracking_data.orderDate,
                                    startLocation=tracking_data.currentLocation, currentLocation=tracking_data.currentLocation, 
                                    targetLocation=tracking_data.targetLocation, distkm= tracking_data.distkm,
                     transportationMethod=transit_method, deliveryEstimateEarly=early, deliveryEstimateLate=late, 
                     orderStatus=tracking_data.orderStatus)
        
        return tracking_item
        

    #use old data to fill in any blanks
    def update_tracking_item(self, old_data: TrackingItem, tracking_data: CreateOrUpdateTracker):

        transit_method = TransitMethod(tracking_data.transporationMethod)
        order_update = datetime.now().strftime(DATE_FORMAT_STR)

        if transit_method.name != old_data.transportationMethod or tracking_data.distkm != old_data.distkm:
            early,late = self.calculate_delivery_estimate(tracking_data.orderDate,
                            tracking_data.distkm, transit_method, True)
        else:
            early = old_data.deliveryEstimateEarly
            late = old_data.deliveryEstimateLate
        
        tracking_item = TrackingItem(username=tracking_data.username, orderNumber=tracking_data.orderNumber, 
                                     parentNumber=tracking_data.parentNumber, orderLastUpdate=order_update,
                                    startLocation=old_data.startLocation, currentLocation=tracking_data.currentLocation,
                     transportationMethod=transit_method.name, deliveryEstimateEarly=early, deliveryEstimateLate=late, 
                     orderStatus=tracking_data.orderStatus)
        
        return tracking_item

    def create_or_update_tracking_item(self, tracking_item: CreateOrUpdateTracker):

        with self.db_connection.cursor() as cur:
            cur.execute(f"SELECT * FROM Tracking WHERE username='{tracking_item.username}' AND orderNumber={tracking_item.orderNumber}")
            row = cur.fetchone()
            if len(row) > 0:
                existing_instance = self.tracking_item_from_row(row)
                return self.update_tracking_item(existing_instance, tracking_item)
            else:
                #do create
                return self.create_tracking_item(tracking_item)
    
    def add_user(self, username: str):
        with self.db_connection.cursor() as cur:
            cur.execute(f"INSERT INTO USER (username) VALUES ({username})")
            self.db_connection.commit()

    def delete_user(self, username):
        query = "DELETE FROM User WHERE username = %s"
        with self.db_connection.cursor() as cur:
            cur.execute(query, (username,))
            self.db_connection.commit()
    
    def delete_order(self, username: str, orderNumber: str):
        query = f"DELETE FROM Tracking WHERE username = {username} AND orderNumber = {orderNumber}"
        with self.db_connection.cursor() as cur:
            cur.execute(query, (username,))
            self.db_connection.commit()

    def connect_rabbitmq(self):
        channel = self.mq_connection_upsert.channel()
        channel.queue_declare(TRACKING_CHANNEL_CREATE_UPDATE)
        def create_update_cb(ch, method, properties, body):
            if type(body) == CreateOrUpdateTracker:
                self.create_or_update_tracking_item(tracking_item=body)
            else:
                print("Error in Upsert thread: bad request")

        channel_del = self.mq_connection_delete.channel()
        channel_del.queue_declare(TRACKING_CHANNEL_DELETE)

        def delete_cb(ch, method, properties, body):
            if type(body) == DeleteOrder:
                self.delete_order(body.username, body.orderNumber)
            elif type(body) == DeleteUser:
                self.delete_user(body.username)
            else:
                print("Error in Deletion thread: bad request")


        self.upsert_thread = PikaReceiver("localhost", TRACKING_CHANNEL_CREATE_UPDATE, create_update_cb)
        self.delete_thread = PikaReceiver("localhost", TRACKING_CHANNEL_DELETE, delete_cb)
        self.upsert_thread.run()
        self.upsert_thread.run()
def run():
    app = FastAPI()
    
    service = TrackingService("localhost", "localhost", "root", "root")
    service.connect_rabbitmq()
    
    def shutdown():
        service.upsert_thread.stop()
        service.delete_thread.stop()
        service.mq_connection_delete.close()
        service.mq_connection_upsert.close()
        service.db_connection.close()
    
    def handle_shutdown(signum, frame):
        shutdown()
        exit(0)
    
    signal.signal(signal.SIGINT, handle_shutdown)   # Ctrl+C
    signal.signal(signal.SIGTERM, handle_shutdown)  # kill / docker stop
    
    
    @app.get("/tracking")
    async def get_order_tracking_data(tracking_req: TrackingReq):
        user = tracking_req.username
        orders = service.get_all_orders(user)
        return {"orders": orders}





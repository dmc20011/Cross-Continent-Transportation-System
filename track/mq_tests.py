import pika
from lib.req_bodies import *

from datetime import datetime
TRACKING_CHANNEL_CREATE_UPDATE = 'Tracking-Updates'
TRACKING_CHANNEL_DELETE = 'Tracking-Delete'

additional_Order_alpha = CreateOrUpdateTracker(
    username="alpha",
    orderNumber="123",
    parentNumber="",
    orderDate=datetime.now().strftime("%Y-%m-%d"),
    currentLocation="China",
    targetLocation="Canada",
    distkm=6000,
    transporationMethod=TransitMethod.Sea,
    orderStatus=OrderStatus.Shipped
)

update_Order_alpha = CreateOrUpdateTracker(
    username="alpha",
    orderNumber="123",
    parentNumber="PAPA",
    orderDate=datetime.now().strftime("%Y-%m-%d"),
    currentLocation="Mexico",
    targetLocation="Canada",
    distkm=2000,
    transporationMethod=TransitMethod.Rail,
    orderStatus=OrderStatus.Shipped
)

additional_Order_charlie = CreateOrUpdateTracker(
    username="charlie",
    orderNumber="A1909",
    parentNumber="ABG",
    orderDate=datetime.now().strftime("%Y-%m-%d"),
    currentLocation="US",
    targetLocation="Canada",
    distkm=1000,
    transporationMethod=TransitMethod.Truck,
    orderStatus=OrderStatus.Shipped
)

del_new_alpha_order = DeleteOrder(username="alpha", orderNumber="123")
del_charlie = DeleteUser(username="charlie")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", port=5672))
channel = connection.channel()
channel.queue_declare(TRACKING_CHANNEL_CREATE_UPDATE,
                      durable=False)
print("MQ Testing begins...")

input("Press ENTER to create new order...")
print(f"Creating: {additional_Order_alpha}")
channel.basic_publish(exchange="", routing_key=TRACKING_CHANNEL_CREATE_UPDATE,
                      body=additional_Order_alpha.model_dump_json().encode())

input("Press ENTER to update order...")
print(f"Updating to: {update_Order_alpha}")
channel.basic_publish(exchange="", routing_key=TRACKING_CHANNEL_CREATE_UPDATE,
                      body=update_Order_alpha.model_dump_json().encode())

input("Press ENTER to create order and user...")
print(f"Creating: {additional_Order_charlie}")
channel.basic_publish(exchange="", routing_key=TRACKING_CHANNEL_CREATE_UPDATE,
                      body=additional_Order_charlie.model_dump_json().encode())

input("Press ENTER to delete order")
print(f"Deleting: {del_new_alpha_order}")
channel.basic_publish(exchange="", routing_key=TRACKING_CHANNEL_DELETE,
                      body=del_new_alpha_order.model_dump_json().encode())

input("Press ENTER to delete order")
print(f"Deleteing: {del_charlie}")
channel.basic_publish(exchange="", routing_key=TRACKING_CHANNEL_DELETE,
                      body=del_charlie.model_dump_json().encode())

print("DONE")

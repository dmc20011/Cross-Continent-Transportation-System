import pika
import pymysql
import threading
import json
import time

CONSOLIDATION_CHANNEL = 'Consolidation-Updates'
NEW_ORDER_CHANNEL = 'New-Order'

MAX_WEIGHT_KG = 1000
MAX_VOLUME_M3 = 10


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
        self.mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

    def connect_to_db(self, host, user, pswd):
        self.connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=pswd,
            database="shipmentdb"
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
                    preferred_transport_mode  VARCHAR(50) DEFAULT 'none',
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

        self.receiver_thread = PikaReceiver("localhost", NEW_ORDER_CHANNEL, on_new_order)
        self.receiver_thread.run()

    def publish_shipment(self, shipment):
        channel = self.mq_connection.channel()
        channel.queue_declare(queue=CONSOLIDATION_CHANNEL)
        channel.basic_publish("", routing_key=CONSOLIDATION_CHANNEL, body=json.dumps(shipment))
        print(f"Published shipment: {shipment}")

    def save_shipment(self, shipment):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO shipments
                   (origin, destination, total_weight_kg, total_volume_m3, order_ids, priority, preferred_transport_mode)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (shipment["origin"], shipment["destination"],
                 shipment["total_weight_kg"], shipment["total_volume_m3"],
                 json.dumps(shipment["order_ids"]),
                 shipment.get("priority", "standard"),
                 shipment.get("preferred_transport_mode", "none"))
            )
        self.connection.commit()
        print(f"Inserted shipment: {shipment['order_ids']}")

    def consolidate(self, orders):
        pass

def run():
    service = ConsolidationService()
    service.connect_to_db("127.0.0.1", "root", "root")
    service.init_db()
    service.test_db()
    service.connect_rabbitmq()

    time.sleep(1)
    service.test_db()
    service.receiver_thread.stop()


if __name__ == "__main__":
    run()

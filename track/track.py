import pika
import pymysql
import threading
import time
TRACKING_CHANNEL = 'Tracking-Updates'
class PikaReceiver(threading.Thread):
    def __init__(self, channel, queue):
        threading.Thread.__init__(self)
        self.channel = channel
        self.stop_event = threading.Event()
        self.queue = queue

    def run(self):
        for method, properties, body in self.channel.consume(self.queue, inactivity_timeout=1):
            if self.stop_event.is_set():
                break

            if not method:
                continue

            print(f"Body: {body}")

    def stop(self):
        self.stop_event.set()

class TrackingService():
    def __init__(self):
        self.mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

    def connect_to_db(self, host, user, pswd):
        self.connection = pymysql.connect(
            host=host,
            port = 3306,
            user=user,
            password=pswd,
            database="trackingdb"
        )

        

    def test_db(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Tracking WHERE username = 'ALPHA'")
            res = cursor.fetchall()
        for item in res:
            print(item)

    def connect_rabbitmq(self):
        channel = self.mq_connection.channel()

        channel.queue_declare(queue='Tracking-Updates')

        channel.queue_declare(TRACKING_CHANNEL)
        self.receiver_thread = PikaReceiver(channel, TRACKING_CHANNEL)
        self.receiver_thread.start()
    

def run():
    service = TrackingService()
    #service.connect_to_db("127.0.0.1", "root", "root")
    #service.test_db()
    service.connect_rabbitmq()
    time.sleep(1)
    channel = pika.BlockingConnection(pika.ConnectionParameters(host='localhost')).channel()
    channel.queue_declare(queue=TRACKING_CHANNEL)
    channel.basic_publish("",routing_key=TRACKING_CHANNEL,body='Hello!')
    time.sleep(1)
    service.receiver_thread.stop()

if __name__ == "__main__":
    run()

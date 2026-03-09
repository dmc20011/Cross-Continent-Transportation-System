import pika
import pymysql
import threading
import time
TRACKING_CHANNEL = 'Tracking-Updates'
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
        def callback(ch, method, properties, body):
            print(f"Got: {body}")
        self.receiver_thread = PikaReceiver("localhost", TRACKING_CHANNEL, callback)
        self.receiver_thread.run()
    

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

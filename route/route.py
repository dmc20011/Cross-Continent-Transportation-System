import time
import pika
import mysql.connector


# program for testing accessibility and functionality of rabbitmq and mariadb instances

def wait(fn, name, retries=20):
    for i in range(retries):
        try:
            fn()
            print(f"{name}: OK")
            return
        except Exception as e:
            print(f"{name}: retry {i+1}/{retries} ({e})")
            time.sleep(2)
    raise RuntimeError(f"{name} failed")


def test_rabbitmq():
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    ch = conn.channel()
    ch.queue_declare(queue="test_queue")
    ch.basic_publish(exchange="", routing_key="test_queue", body="test")
    conn.close()


def test_db(host):
    conn = mysql.connector.connect(
        host=host,
        port=3306,
        user="root",
        password="mypass",
    )
    cur = conn.cursor()
    cur.execute("SELECT 1")
    cur.fetchone()
    conn.close()


if __name__ == "__main__":
    wait(test_rabbitmq, "rabbitmq")
    wait(lambda: test_db("shipmentdb"), "shipmentdb")
    wait(lambda: test_db("orderdb"), "orderdb")
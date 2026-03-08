import pika
import pymysql

class TrackingService():
    def __init__(self):
        pass

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

    def connect_rabbitmq():
    

def run():
    service = TrackingService()
    service.connect_to_db("127.0.0.1", "root", "root")
    service.test_db()

if __name__ == "__main__":
    run()

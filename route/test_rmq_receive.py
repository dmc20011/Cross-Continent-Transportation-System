import pika

# RabbitMQ connection parameters
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'Tracking-Updates'

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()

# Ensure the queue exists
channel.queue_declare(queue=QUEUE_NAME)

# Callback function to handle messages
def callback(ch, method, properties, body):
    print("Received message:", body.decode())  # body is bytes
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Subscribe to the queue
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

print("Waiting for messages. To exit press CTRL+C")
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping...")
    channel.stop_consuming()
    connection.close()
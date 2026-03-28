import pika
import json

CONSOLIDATION_CHANNEL = "Consolidation-Updates"

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()

channel.queue_declare(queue=CONSOLIDATION_CHANNEL)

message = {
    "origin": "Toronto",
    "destination": "Sydney",
    "priority": "Standard",
    "transport_method": "None"
}

channel.basic_publish(
    exchange='',
    routing_key=CONSOLIDATION_CHANNEL,
    body=json.dumps(message)
)

print("Message sent!")

connection.close()

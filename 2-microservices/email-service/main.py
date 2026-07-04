from dotenv import load_dotenv
import os

load_dotenv()


from confluent_kafka import Consumer
import json
import time

conf = {
    'bootstrap.servers': f"{os.getenv('KAFKA_HOST')}:{os.getenv('KAFKA_PORT')}",
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'sasl.username': os.getenv('KAFKA_USERNAME'),
    'sasl.password': os.getenv('KAFKA_PASSWORD'),
    'ssl.ca.location': 'ca.pem',
    'group.id': 'email-service-group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(conf)
consumer.subscribe(['order_placed'])

print("email-service: listening for orders...")

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue

        order = json.loads(msg.value().decode('utf-8'))

        print(f"[EMAIL] Sending confirmation to {order['customer_email']}...")
        time.sleep(1)  # simulate calling a real email API
        print(f"[EMAIL] Email sent for order: {order['product']}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
from dotenv import load_dotenv
import os

load_dotenv()


from confluent_kafka import Consumer
from database import SessionLocal, Order
import json
import time

conf = {
    'bootstrap.servers': f"{os.getenv('KAFKA_HOST')}:{os.getenv('KAFKA_PORT')}",
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'sasl.username': os.getenv('KAFKA_USERNAME'),
    'sasl.password': os.getenv('KAFKA_PASSWORD'),
    'ssl.ca.location': 'ca.pem',
    'group.id': 'payment-service-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['order_placed'])

print("payment-service: listening for orders...")

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue

        order = json.loads(msg.value().decode('utf-8'))
        order_id = order['order_id']

        print(f"[PAYMENT] Charging {order['amount']} for {order['product']} (order #{order_id})...")
        time.sleep(2)

        # Update the order's status in the database
        db = SessionLocal()
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if db_order:
            db_order.status = "paid"
            db.commit()
            print(f"[PAYMENT] Order #{order_id} marked as paid.")
        else:
            print(f"[PAYMENT] Warning: order #{order_id} not found in database.")
        db.close()

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
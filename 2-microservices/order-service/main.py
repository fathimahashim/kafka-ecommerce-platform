from dotenv import load_dotenv
import os

load_dotenv()


from fastapi import FastAPI
from pydantic import BaseModel
from confluent_kafka import Producer
from database import SessionLocal, Order
import json

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local dev; restrict this in production
    allow_methods=["*"],
    allow_headers=["*"],
)
producer = Producer({
    'bootstrap.servers': f"{os.getenv('KAFKA_HOST')}:{os.getenv('KAFKA_PORT')}",
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'sasl.username': os.getenv('KAFKA_USERNAME'),
    'sasl.password': os.getenv('KAFKA_PASSWORD'),
    'ssl.ca.location': 'ca.pem',
})


class OrderRequest(BaseModel):
    customer_email: str
    product: str
    quantity: int
    amount: float


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Event delivered to topic '{msg.topic()}'")


@app.post("/orders")
def place_order(order: OrderRequest):
    db = SessionLocal()

    new_order = Order(
        customer_email=order.customer_email,
        product=order.product,
        quantity=order.quantity,
        amount=order.amount,
        status="pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    db.close()

    event = {
        "order_id": new_order.id,
        "customer_email": order.customer_email,
        "product": order.product,
        "quantity": order.quantity,
        "amount": order.amount
    }
    producer.produce(
        topic='order_placed',
        key=order.customer_email,
        value=json.dumps(event),
        callback=delivery_report
    )
    producer.flush()

    return {"status": "success", "order_id": new_order.id}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    db.close()

    if not order:
        return {"error": "Order not found"}

    return {
        "id": order.id,
        "customer_email": order.customer_email,
        "product": order.product,
        "quantity": order.quantity,
        "amount": order.amount,
        "status": order.status,
        "created_at": order.created_at.isoformat()
    }
from fastapi import FastAPI
from pydantic import BaseModel
import time

app = FastAPI()

# ---- Data model for an incoming order ----
class OrderRequest(BaseModel):
    customer_email: str
    product: str
    quantity: int
    amount: float


# ---- These simulate other "departments" of the business ----
def process_payment(order: OrderRequest):
    print(f"[PAYMENT] Charging {order.amount} for {order.product}...")
    time.sleep(2)  # pretend this calls a real payment gateway (slow!)
    print("[PAYMENT] Payment successful.")


def send_confirmation_email(order: OrderRequest):
    print(f"[EMAIL] Sending confirmation to {order.customer_email}...")
    time.sleep(1)  # pretend this calls a real email API (also slow!)
    print("[EMAIL] Email sent.")


def log_order_analytics(order: OrderRequest):
    print(f"[ANALYTICS] Logging order: {order.product} x{order.quantity}")


# ---- The single endpoint that does EVERYTHING ----
@app.post("/orders")
def place_order(order: OrderRequest):
    print(f"\n--- New order received: {order.product} ---")

    process_payment(order)
    send_confirmation_email(order)
    log_order_analytics(order)

    print("--- Order complete ---\n")
    return {"status": "success", "message": "Order placed successfully"}

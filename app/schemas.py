# app/schemas.py
from pydantic import BaseModel

class CheckoutSessionCreate(BaseModel):
    plan: str
    quantity: int = 1

class SubscriptionOut(BaseModel):
    user_id: int
    plan_name: str
    current_status: str
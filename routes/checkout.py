from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import stripe
import os

from app.config import STRIPE_SECRET_KEY
from app.services.auth_service import validate_user
from app.services.subscription_service import PRICE_IDS

router = APIRouter()

class CheckoutRequest(BaseModel):
    user_id: str
    tier: str
    success_url: str
    cancel_url: str
    token: str

@router.post("/create-checkout-session")
def create_checkout_session(payload: CheckoutRequest):
    """
    POST /create-checkout-session
    Request Body:
    {
      "user_id": "<user_id>",
      "tier": "Gold/Silver/Bronze",
      "success_url": "<URL>",
      "cancel_url": "<URL>",
      "token": "<auth_token>"
    }
    """
    # 1. Validate user with auth service
    is_valid_user = validate_user(payload.user_id, payload.token)
    if not is_valid_user:
        raise HTTPException(status_code=401, detail="Invalid user or token")

    # 2. Get Price ID for the given tier
    price_id = PRICE_IDS.get(payload.tier)
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")

    # 3. Create Stripe Checkout Session
    stripe.api_key = STRIPE_SECRET_KEY
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=payload.success_url,
            cancel_url=payload.cancel_url,
            # Optionally store user_id in metadata
            metadata={"user_id": payload.user_id, "tier": payload.tier},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 4. Return checkout URL
    return {"checkout_url": checkout_session.url}
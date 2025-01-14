from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import stripe
import os

from app.config import STRIPE_WEBHOOK_SECRET
from app.services.subscription_service import update_subscription_status

router = APIRouter()

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events, such as:
      - checkout.session.completed
      - invoice.payment_failed
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        tier = session.get("metadata", {}).get("tier", "Unknown")
        update_subscription_status(user_id, "active", tier)

    elif event_type == "invoice.payment_failed":
        invoice = event["data"]["object"]
        user_id = invoice.get("metadata", {}).get("user_id")
        tier = invoice.get("metadata", {}).get("tier", "Unknown")
        update_subscription_status(user_id, "payment_failed", tier)

    return {"status": "success"}
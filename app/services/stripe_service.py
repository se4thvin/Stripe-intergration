# app/services/stripe_service.py
import os
import stripe
from fastapi import HTTPException

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
DOMAIN_URL = os.getenv("DOMAIN_URL", "https://coursebite.ai")

# Example: map your 3 tiers to Stripe Price IDs
PLAN_PRICE_MAPPING = {
    "bronze": "priceIDXXXXXX_bronze",
    "silver": "PriceIDXXXXXX_silver",
    "gold":   "PriceIDXXXXXX_gold"
}

def create_stripe_checkout_session(plan: str, quantity: int):
    """Create a subscription checkout session for the given plan & quantity."""
    price_id = PLAN_PRICE_MAPPING.get(plan.lower())
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid plan selected.")

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            success_url=f"{DOMAIN_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{DOMAIN_URL}/cancel",
            line_items=[{"price": price_id, "quantity": quantity}],
        )
        return session.url
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def verify_stripe_signature(payload: bytes, signature: str):
    """Verify the incoming webhook signature (if configured)."""
    if not WEBHOOK_SECRET:
        # If you don't set a secret, can't verify signature
        return stripe.Event.construct_from({}, stripe.api_key)

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=WEBHOOK_SECRET
        )
        return event
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")
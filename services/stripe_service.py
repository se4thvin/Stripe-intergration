# app/services/stripe_service.py
import os
import stripe
from fastapi import Request
from fastapi import HTTPException

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

def create_stripe_customer(email: str) -> str:
    """Create a new Stripe customer and return its ID."""
    customer = stripe.Customer.create(email=email)
    return customer.id

def create_stripe_checkout_session(
    stripe_customer_id: str,
    tier: str,
    success_url: str,
    cancel_url: str,
    user_id: int
) -> str:
    """Create a Stripe subscription checkout session for the given tier."""
    # Map your tiers to price IDs from the Stripe dashboard
    price_mapping = {
        "Bronze": "price_XXXX_Bronze",
        "Silver": "price_XXXX_Silver",
        "Gold":   "price_XXXX_Gold"
    }
    price_id = price_mapping.get(tier)
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")

    session = stripe.checkout.Session.create(
        customer=stripe_customer_id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"user_id": str(user_id)}
    )
    return session.url

async def verify_stripe_signature(request: Request) -> dict:
    """Verify Stripe's webhook signature and return the event object."""
    signature = request.headers.get("stripe-signature")
    if not signature:
        return None

    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=STRIPE_WEBHOOK_SECRET
        )
        return event
    except stripe.error.SignatureVerificationError:
        return None
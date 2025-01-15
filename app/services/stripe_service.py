# app/services/stripe_service.py
import os
import stripe
from fastapi import HTTPException

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

def get_price_by_lookup_key(lookup_key: str) -> str:
    """
    Retrieve a Price object from Stripe by a known 'lookup_key',
    then return the associated price ID. 
    """
    try:
        prices = stripe.Price.list(
            lookup_keys=[lookup_key],
            expand=['data.product']
        )
        if not prices.data:
            return None
        return prices.data[0].id
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def create_checkout_session(price_id: str, domain: str) -> str:
    """
    Creates a subscription session with optional trial, automatic tax, etc.
    Returns the session.url for redirect.
    """
    try:
        session = stripe.checkout.Session.create(
            line_items=[{"price": price_id, "quantity": 1}],
            mode='subscription',
            success_url=f"{domain}?success=true&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{domain}?canceled=true",
            subscription_data={"trial_period_days": 7},
            automatic_tax={"enabled": True},
        )
        return session.url
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
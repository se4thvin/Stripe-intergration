# app/routers/subscription.py
import os
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from app.services.stripe_service import get_price_by_lookup_key, create_checkout_session

router = APIRouter()

YOUR_DOMAIN = os.getenv("YOUR_DOMAIN", "http://localhost:4242")

@router.post("/create-checkout-session")
def create_checkout(lookup_key: str = Form(...)):
    """
    Adapted from the Flask example:
      1) Retrieve the price ID via the lookup_key.
      2) Create a Stripe Checkout Session in subscription mode.
      3) Return a 303 redirect to the session.url (or handle differently).
    """
    try:
        # Step 1: Get Price from Stripe
        price_id = get_price_by_lookup_key(lookup_key)
        if not price_id:
            raise HTTPException(status_code=404, detail="Price not found for that lookup key")

        # Step 2: Create a subscription checkout session
        checkout_url = create_checkout_session(price_id, YOUR_DOMAIN)

        # Step 3: Return a redirect
        return RedirectResponse(url=checkout_url, status_code=303)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Server error")
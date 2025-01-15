# app/routers/portal.py
import os
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
import stripe

router = APIRouter()

YOUR_DOMAIN = os.getenv("YOUR_DOMAIN", "http://localhost:4242")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

@router.post("/create-portal-session")
def create_portal_session(session_id: str = Form(...)):
    """
    Similar to the Flask route:
      1) Retrieve the Checkout session by its ID.
      2) Create a billing portal session for its customer.
      3) Redirect to the portal URL.
    """
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        portal_session = stripe.billing_portal.Session.create(
            customer=checkout_session.customer,
            return_url=YOUR_DOMAIN
        )
        return RedirectResponse(url=portal_session.url, status_code=303)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to create portal session")
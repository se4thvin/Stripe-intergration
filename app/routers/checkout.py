# app/routers/checkout.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.stripe_service import create_stripe_checkout_session

router = APIRouter()

@router.post("/create-checkout-session")
async def create_checkout_session(
    plan: str = Form(...),
    quantity: int = Form(1),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # If you have an auth flow
):
    """
    1. Confirm user is logged in or handle user creation.
    2. Create a subscription checkout session on Stripe.
    3. Redirect the user to the session URL.
    """
    # Example: If user isn't logged in, raise an HTTPException or redirect

    try:
        checkout_url = create_stripe_checkout_session(plan, quantity)
        return RedirectResponse(url=checkout_url, status_code=303)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
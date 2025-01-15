# app/routers/subscription.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.auth_service import get_current_user, update_user_in_auth_service
from app.services.stripe_service import create_stripe_customer, create_stripe_checkout_session

router = APIRouter()

class SubscribeRequest(BaseModel):
    tier: str
    success_url: str
    cancel_url: str

@router.post("/subscribe")
def subscribe(
    req: SubscribeRequest,
    token: str = Query(..., description="Bearer token from auth-service")
):
    """
    1. Validate the user's token with the auth-service (get_current_user).
    2. Check for or create stripe_customer_id in Stripe.
    3. Create a checkout session for the chosen tier.
    4. Return the session URL.
    """
    # 1) Validate and retrieve user
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token or user not found.")

    user_id = user["id"]
    email = user.get("email")
    stripe_customer_id = user.get("stripe_customer_id")

    if not email:
        raise HTTPException(status_code=400, detail="User has no email on file.")

    # 2) If no Stripe customer ID, create one
    if not stripe_customer_id:
        stripe_customer_id = create_stripe_customer(email)
        # Update user in auth-service
        update_user_in_auth_service(user_id, {"stripe_customer_id": stripe_customer_id})

    # 3) Create checkout session
    checkout_url = create_stripe_checkout_session(
        stripe_customer_id=stripe_customer_id,
        tier=req.tier,
        success_url=req.success_url,
        cancel_url=req.cancel_url,
        user_id=user_id
    )

    return {"checkout_url": checkout_url}
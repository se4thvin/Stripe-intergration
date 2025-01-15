from fastapi import APIRouter, Request, HTTPException
from app.services.stripe_service import verify_stripe_signature
from app.services.auth_service import update_user_in_auth_service

router = APIRouter()

@router.post("/callback")
async def webhook_callback(request: Request):
    """
    Receives Stripe webhook events:
    - checkout.session.completed -> activate user subscription
    - invoice.payment_failed -> handle failed renewals
    """
    event = await verify_stripe_signature(request)

    if event is None:
        raise HTTPException(status_code=400, detail="Invalid or missing Stripe signature")

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        session_data = event["data"]["object"]
        user_id_str = session_data["metadata"].get("user_id")
        if user_id_str:
            update_user_in_auth_service(int(user_id_str), {"subscription_status": "active"})

    elif event_type == "invoice.payment_failed":
        # Retrieve subscription, find user, or store subscription data in metadata
        # Optionally mark them as "past_due"
        pass

    return {"status": "success"}
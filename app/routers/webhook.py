# app/routers/webhook.py
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.stripe_service import verify_stripe_signature
from app.services.subscription_logic import (
    activate_subscription, mark_subscription_past_due, cancel_subscription
)

router = APIRouter()

@router.post("")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Stripe sends events here. We'll:
     - Verify signature
     - Parse event type
     - Update DB accordingly
    """
    signature = request.headers.get("stripe-signature")
    payload = await request.body()

    # 1) Verify the signature
    try:
        event = verify_stripe_signature(payload, signature)
    except HTTPException as e:
        raise e

    event_type = event["type"]
    data_obj = event["data"]["object"]

    print(f"Received event: {event_type}")

    # 2) Handle relevant events
    if event_type == "checkout.session.completed":
        """
        Occurs when checkout completes. 
        This means a Subscription was created if 'mode=subscription'.
        data_obj might look like: {
           id: ...
           subscription: 'sub_XXXXXXX',
           ...
        }
        """
        subscription_id = data_obj.get("subscription")
        # You might retrieve the user ID from your 'metadata' or from your DB
        # If you set "metadata={'user_id': <id>}" in create_session, you'd read it here:
        user_id = data_obj.get("metadata", {}).get("user_id")

        if subscription_id and user_id:
            # For example, "plan" might be stored on your side if you added metadata
            # or you can fetch from the subscription object on Stripe
            # For brevity, let's assume you already know the plan or have a default
            plan = "gold"  # or parse from data

            activate_subscription(db, int(user_id), plan, subscription_id)

    elif event_type in ("invoice.payment_succeeded", "invoice.paid"):
        """
        For recurring payments. 
        data_obj has "subscription" and more info about the invoice.
        """
        subscription_id = data_obj.get("subscription")
        # If you store subscription => user mappings, query that or store sub in DB
        # Then confirm the user is still active and extend their access if needed
        print("Payment succeeded. Keep user active or update next billing date.")

    elif event_type == "invoice.payment_failed":
        """
        Payment for the recurring subscription failed.
        Mark sub as 'past_due' or notify user to update payment info.
        """
        subscription_id = data_obj.get("subscription")
        print("Payment failed. Possibly mark subscription as past due.")
        # If you have user_id from DB, call `mark_subscription_past_due(db, user_id)`

    elif event_type == "customer.subscription.deleted":
        """
        Subscription canceled or ended. Revoke access.
        """
        subscription_id = data_obj.get("id")
        print("Subscription canceled or ended.")
        # If we know the user, call `cancel_subscription(db, user_id)`

    # You can handle other events like "customer.subscription.updated" or "invoice.upcoming"
    # as needed for your flow.

    return JSONResponse({"status": "success"})
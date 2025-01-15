# app/routers/webhook.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import os, json, stripe

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

@router.post("")
async def webhook_received(request: Request):
    """
    1) Verify webhook signature if WEBHOOK_SECRET is set
    2) Parse event type and handle accordingly
    """
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    event = None

    if WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, WEBHOOK_SECRET
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Webhook Error: {e}")
    else:
        # If no signing secret is configured, just parse the JSON
        event = json.loads(payload)

    event_type = event["type"]
    data_object = event["data"]["object"]

    print("Event Type:", event_type)

    if event_type == "checkout.session.completed":
        print("Payment succeeded!")
        # TODO: post-payment logic here (e.g., mark subscription as active)
    elif event_type == "customer.subscription.trial_will_end":
        print("Subscription trial will end soon.")
    elif event_type == "customer.subscription.created":
        print(f"Subscription created: {event['id']}")
    elif event_type == "customer.subscription.updated":
        print(f"Subscription updated: {event['id']}")
    elif event_type == "customer.subscription.deleted":
        print(f"Subscription canceled: {event['id']}")
    elif event_type == "entitlements.active_entitlement_summary.updated":
        print(f"Entitlements updated: {event['id']}")
    else:
        print("Unhandled event type:", event_type)

    return JSONResponse({"status": "success"})
# app/main.py
import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.routers import subscription, webhook

# Load env variables from .env file (in production, you might rely on the OS environment)
load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Subscription Service",
        description="Handles Stripe subscription flows",
        version="1.0.0"
    )

    # Mount routers
    app.include_router(subscription.router, prefix="/subscriptions", tags=["subscription"])
    app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])

    @app.get("/")
    def root():
        return {"message": "Subscription microservice is running."}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
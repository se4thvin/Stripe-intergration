# app/main.py
import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.routers import subscription, portal, webhook

load_dotenv()  # Reads from .env

def create_app() -> FastAPI:
    app = FastAPI(title="Stripe Subscription Service")

    # Include Routers
    app.include_router(subscription.router, prefix="/checkout", tags=["checkout"])
    app.include_router(portal.router, prefix="/portal", tags=["portal"])
    app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])

    @app.get("/")
    def index():
        return {"message": "Subscription service is running."}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", port=4242, host="0.0.0.0", reload=True)
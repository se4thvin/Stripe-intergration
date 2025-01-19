# app/main.py
import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.database import Base, engine
from app.routers import checkout, webhook

def create_app() -> FastAPI:
    load_dotenv()
    # Create DB tables if they don't exist
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="Coursebite Subscription Service")

    # Mount the routes
    app.include_router(checkout.router, prefix="/checkout", tags=["Checkout"])
    app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])

    @app.get("/")
    def read_root():
        return {"message": "Coursebite Subscription Service Running"}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=4242, reload=True)
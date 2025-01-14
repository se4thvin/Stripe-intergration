from fastapi import FastAPI
from .routes.checkout import router as checkout_router
from .routes.webhook import router as webhook_router

# Create the FastAPI application
app = FastAPI(title="Subscription Service", version="1.0.0")

# Register our routers
app.include_router(checkout_router, prefix="")
app.include_router(webhook_router, prefix="")

# For local testing (not typically needed if using uvicorn/gunicorn entrypoints)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
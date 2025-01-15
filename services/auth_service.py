# app/services/auth_service.py
import os
import requests
from fastapi import HTTPException

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

def get_current_user(token: str):
    """
    Sends a GET request to auth-service (/users/me) 
    with the Bearer token to validate & fetch user data.
    """
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{AUTH_SERVICE_URL}/users/me/", headers=headers, timeout=5)
    if resp.status_code != 200:
        return None
    return resp.json()

def update_user_in_auth_service(user_id: int, data: dict):
    """
    PATCH the user's record to store stripe_customer_id or subscription_status.
    e.g. /users/{user_id}/update_stripe_info
    """
    url = f"{AUTH_SERVICE_URL}/users/{user_id}/update_stripe_info"
    resp = requests.patch(url, json=data, timeout=5)
    if resp.status_code not in (200, 204):
        raise HTTPException(status_code=400, detail="Failed to update user in auth service.")
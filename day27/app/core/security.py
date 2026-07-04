from fastapi import Header, HTTPException, status
from app.config import settings

def verify_token(x_webhook_token: str = Header(..., description="Secret token for authentication")):
    if x_webhook_token != settings.webhook_secret_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing webhook token"
        )
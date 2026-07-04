import httpx
import logging
from app.config import settings

logger = logging.getLogger("webhook.slack")

async def post_to_slack(summary: str, source: str) -> bool:
    
    payload = {
        "text": f"*New AI Pipeline Alert from {source.upper()}*\n\n{summary}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.slack_webhook_url, 
                json=payload,
                timeout=5.0
            )
        
        if response.status_code == 200:
            logger.info("Successfully posted message to Slack.")
            return True
        else:
            logger.error(f"Slack returned non-200 status: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to connect to Slack Webhook: {e}")
        return False
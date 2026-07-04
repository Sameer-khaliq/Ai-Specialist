from fastapi import APIRouter, Depends, HTTPException, status
import uuid
import logging

from app.models.schemas import WebhookPayload, ProcessingResult
from app.services.ai_processor import process_form_data
from app.services.slack_notifier import post_to_slack
from app.core.security import verify_token
from app.utils.idempotency import is_duplicate

router = APIRouter()
logger = logging.getLogger("webhook.route")

@router.post("/webhook", response_model = ProcessingResult, dependencies = [Depends(verify_token)])

async def handle_webhook(payload : WebhookPayload):
    request_id = payload.request_id or str (uuid.uuid4())

    if is_duplicate(request_id):
        logger.warning(f"Duplicate request detected and blocked!  Request_id: {request_id}")
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "Duplicate request detected !!!"
        )
    logger.info(f"Processing webhook request {request_id} from source: {payload.source}")

    try:
        summary = process_form_data(payload.form_data)
    except Exception as e:
        logger.error(f"AI Core processing failed for request {request_id}: {e}")
    
        await post_to_slack(f" *Pipeline Failure Alert* \nProcessing failed for request ID `{request_id}`. Error: {str(e)}", payload.source)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI processing engine failure"
        )
    
    # Slack Notification Layer
    slack_ok = await post_to_slack(summary, payload.source)
    if not slack_ok:
        logger.warning(f"Message processed but failed to post to Slack for request {request_id}")

    return ProcessingResult(
        request_id=request_id,
        status="success",
        ai_summary=summary,
        slack_posted=slack_ok,
        notion_logged=False  
    )
from pydantic import BaseModel, Field
from typing import Optional

class WebhookPayload(BaseModel):
    source: str = Field(..., description="E.g., 'zapier', 'make', ya 'google_forms'")  # ... shows this field is strictly required
    form_data: dict = Field(..., description="Raw dictionary content jo input form se mila")
    request_id: Optional[str] = Field(None, description="Unique string for idempotency tracking")

class ProcessingResult(BaseModel):
    request_id: str = Field(..., description="Unique string for idempotency tracking")
    status: str = Field(..., description="Status of the processing")
    ai_summary: str = Field(..., description="AI-generated summary of the form data")
    slack_posted: bool = Field(..., description="Whether the result was posted to Slack")
    notion_logged: bool = Field(..., description="Whether the result was logged to Notion") 
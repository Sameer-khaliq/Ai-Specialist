"""
Tests for the /webhook route end-to-end (with mocked AI + Slack calls).
Run with: pytest tests/test_webhook_route.py -v
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

VALID_HEADERS = {"x-webhook-token": settings.webhook_secret_token}


def test_health_check():
    """Basic health check endpoint should work without auth."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_webhook_rejects_missing_token():
    """Requests without the webhook secret token should be rejected."""
    response = client.post(
        "/api/v1/webhook",
        json={"source": "manual_test", "form_data": {"name": "Ali"}}
    )
    assert response.status_code in (401, 422)  # 422 if header missing entirely


def test_webhook_rejects_wrong_token():
    """Requests with an incorrect token should return 401."""
    response = client.post(
        "/api/v1/webhook",
        headers={"x-webhook-token": "wrong-token"},
        json={"source": "manual_test", "form_data": {"name": "Ali"}}
    )
    assert response.status_code == 401


@patch("app.routes.webhook.post_to_slack", new_callable=AsyncMock)
@patch("app.routes.webhook.process_form_data")
def test_webhook_success_flow(mock_ai, mock_slack):
    """
    Full happy path: valid token, valid payload, AI processing succeeds,
    Slack post succeeds.
    """
    mock_ai.return_value = "Customer reports damaged order, requests replacement."
    mock_slack.return_value = True

    response = client.post(
        "/api/v1/webhook",
        headers=VALID_HEADERS,
        json={
            "source": "make_production_demo",
            "form_data": {"name": "Ali Raza", "issue": "Order arrived damaged"},
            "request_id": "test-request-001"
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["slack_posted"] is True
    assert "damaged" in body["ai_summary"].lower()


@patch("app.routes.webhook.process_form_data")
def test_webhook_handles_ai_failure_gracefully(mock_ai):
    """If the AI call throws, the endpoint should return 502, not crash."""
    mock_ai.side_effect = Exception("Gemini API timeout")

    response = client.post(
        "/api/v1/webhook",
        headers=VALID_HEADERS,
        json={
            "source": "manual_test",
            "form_data": {"name": "Test User", "issue": "Some issue"},
            "request_id": "test-request-002"
        }
    )

    assert response.status_code == 502


def test_webhook_rejects_duplicate_request_id():
    """Same request_id sent twice should be rejected the second time."""
    payload = {
        "source": "manual_test",
        "form_data": {"name": "Dup Test", "issue": "Testing idempotency"},
        "request_id": "duplicate-test-id-999"
    }

    with patch("app.routes.webhook.process_form_data", return_value="summary"), \
         patch("app.routes.webhook.post_to_slack", new_callable=AsyncMock) as mock_slack:
        mock_slack.return_value = True
        first = client.post("/api/v1/webhook", headers=VALID_HEADERS, json=payload)
        second = client.post("/api/v1/webhook", headers=VALID_HEADERS, json=payload)

    assert first.status_code == 200
    assert second.status_code == 409
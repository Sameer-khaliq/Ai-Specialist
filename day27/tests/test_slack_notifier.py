"""
Tests for the Slack notifier service.
Uses mocking so tests don't actually hit Slack's real API.
Run with: pytest tests/test_slack_notifier.py -v
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.slack_notifier import post_to_slack


@pytest.mark.asyncio
async def test_post_to_slack_success():
    """Should return True when Slack responds with 200."""
    mock_response = AsyncMock()
    mock_response.status_code = 200

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await post_to_slack("Test summary", "manual_test")
        assert result is True


@pytest.mark.asyncio
async def test_post_to_slack_failure():
    """Should return False when Slack responds with a non-200 status."""
    mock_response = AsyncMock()
    mock_response.status_code = 500

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await post_to_slack("Test summary", "manual_test")
        assert result is False


@pytest.mark.asyncio
async def test_post_to_slack_includes_source_in_message():
    """The posted payload should reference the source system (e.g. Make.com)."""
    captured_payload = {}

    async def fake_post(url, json, **kwargs):
        captured_payload.update(json)
        mock_response = AsyncMock()
        mock_response.status_code = 200
        return mock_response

    with patch("httpx.AsyncClient.post", side_effect=fake_post):
        await post_to_slack("Order issue summary", "make_production_demo")

    assert "make_production_demo" in captured_payload.get("text", "").lower()
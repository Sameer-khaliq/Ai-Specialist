# Webhook-Based AI Pipeline

A production-style automation pipeline that receives form submissions via webhook (from Make.com or Zapier), processes them with an LLM, and posts a structured summary directly to Slack — end to end in under 30 seconds.

**Client-facing pitch:** Submit a form → AI reads and summarizes it → your team sees the result in Slack instantly. No manual triage, no missed context.

---

## Demo Flow

```
Form submission (Google Form / any form)
        ↓
Make.com (or Zapier) webhook trigger
        ↓
FastAPI endpoint (this project)
        ↓
AI processing — Groq (Llama-3.3-70B)
        ↓
Slack notification (Incoming Webhook)
```

---

## Why This Matters (Freelance Angle)

Most businesses collect form submissions (support requests, leads, feedback) and have someone manually read through them to figure out priority and next steps. This pipeline automates that first triage step — the AI reads the submission and tells the team what it's about and how urgent it is, before a human even opens it.

This is a genuinely reusable pattern: swap the Slack destination for email or Notion, swap the prompt for a different business need (lead qualification, support ticket routing, feedback categorization), and the same architecture applies.

---

## Requirements

### Functional Requirements
| ID | Requirement |
|---|---|
| FR1 | Expose a webhook endpoint that accepts JSON payloads from Make.com/Zapier |
| FR2 | Validate incoming payload structure before processing |
| FR3 | Process form content using an LLM to produce a concise summary |
| FR4 | Post the AI summary to a Slack channel via Incoming Webhook |
| FR5 | Report failures back to Slack (not just fail silently) |

### Non-Functional Requirements
| ID | Requirement | How it's addressed |
|---|---|---|
| NFR1 | Reliability | AI/Slack calls wrapped in error handling; failures return proper HTTP errors instead of crashing |
| NFR2 | Security | Webhook endpoint requires a shared secret token (`x-webhook-token` header) |
| NFR3 | Observability | Structured logging on every request (timestamp, source, status) |
| NFR4 | Idempotency | Duplicate `request_id` values are rejected (409) to prevent duplicate Slack posts |
| NFR5 | Performance | Endpoint responds within a few seconds under normal conditions (Groq backend chosen partly for low latency) |
| NFR6 | Config separation | All secrets/config loaded from `.env`, never hardcoded |
| NFR7 | Testability | Business logic separated into `services/` — independently testable without spinning up the full API |

---

## Tech Stack
- **FastAPI** — webhook endpoint + routing
- **Groq (Llama-3.3-70B)** — AI processing (swapped in after hitting Gemini free-tier limits; also faster)
- **Slack Incoming Webhooks** — result delivery
- **Make.com** — trigger/automation layer connecting forms to this API
- **Pydantic** — request/response validation and settings management
- **pytest / pytest-asyncio** — unit and integration testing (mocked external calls)

---

## Project Structure
```
day27/
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── config.py                 # Centralized settings (.env-driven)
│   ├── models/
│   │   └── schemas.py              # Request/response Pydantic models
│   ├── services/
│   │   ├── ai_processor.py          # Groq LLM call logic
│   │   └── slack_notifier.py         # Slack webhook posting logic
│   ├── routes/
│   │   └── webhook.py                 # POST /api/v1/webhook
│   ├── core/
│   │   ├── security.py                 # Shared-secret token verification
│   │   └── logging_config.py            # Structured logging setup
│   └── utils/
│       └── idempotency.py                # Duplicate request_id detection
├── tests/
│   ├── test_ai_processor.py               # Tests real Groq integration
│   ├── test_slack_notifier.py              # Tests Slack posting (mocked)
│   └── test_webhook_route.py                # Tests full endpoint flow (mocked)
├── docs/
│   └── architecture.md                       # Detailed flow + design decisions
├── .env.example
└── README.md
```

---

## Setup

1. Install dependencies:
```
uv add fastapi uvicorn pydantic pydantic-settings httpx python-dotenv groq
uv add pytest pytest-asyncio --dev
```

2. Copy `.env.example` to `.env` and fill in:
```
GROQ_API_KEY=your_key_here
SLACK_WEBHOOK_URL=your_slack_incoming_webhook_url
WEBHOOK_SECRET_TOKEN=your_own_secret_string
```

3. Run the server:
```
uv run uvicorn app.main:app --reload
```

4. Expose it publicly for Make.com/Zapier (local dev only):
```
ngrok http 8000
```

5. In Make.com, set the webhook action to POST to:
```
https://<your-ngrok-url>/api/v1/webhook
```
with header `x-webhook-token: <your secret>` and a JSON body matching:
```json
{
  "source": "make_production_demo",
  "form_data": { "name": "...", "issue": "..." },
  "request_id": "unique-id-here"
}
```

---

## Testing

Run the full suite:
```
uv run pytest tests/ -v
```

- `test_ai_processor.py` calls the real Groq API (confirms live integration works)
- `test_slack_notifier.py` and `test_webhook_route.py` use mocked HTTP calls — no real Slack messages are sent during testing

All 9 tests passing, covering: successful end-to-end flow, missing/invalid auth token, AI failure handling, and duplicate request rejection.

---

## Known Limitations / Next Steps
- Idempotency store is in-memory (resets on server restart) — a production version would use Redis
- Notion logging was scoped as a stretch goal, not yet implemented
- No retry logic on transient Slack/Groq failures yet (observed one transient Groq connection error during Day 26 benchmarking — worth handling explicitly here too)
- Deployment is currently local + ngrok for demo purposes; a real client deployment would use a persistent host (Railway, Render, etc.)
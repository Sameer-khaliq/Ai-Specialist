# Architecture — Webhook AI Pipeline

## 1. Overview

This system exists to remove manual triage from form-based workflows. A form is submitted somewhere (Google Form, website contact form, etc.), an automation platform (Make.com) catches that event and forwards it to our API, our API asks an LLM to make sense of it, and the result lands directly in Slack — ready for a human to act on, not read through raw data first.

The design goal was not just "call an AI and post to Slack." It was to build this the way a real backend service should be built: validated inputs, authenticated access, observable behavior, graceful failure, and testable components — so that this pipeline could plausibly sit in front of a paying client's real workflow, not just a demo.

---

## 2. End-to-End Flow

```
┌─────────────────┐     ┌─────────────┐     ┌──────────────────────┐     ┌───────────┐     ┌───────┐
│  Form Submission │ --> │  Make.com   │ --> │  FastAPI /webhook     │ --> │  Groq LLM │ --> │ Slack │
│ (Google Form etc)│     │  (webhook)  │     │  (validate + auth)    │     │ (summary) │     │ (post)│
└─────────────────┘     └─────────────┘     └──────────────────────┘     └───────────┘     └───────┘
                                                        │
                                                        ▼
                                              Idempotency check
                                              (reject duplicates)
                                                        │
                                                        ▼
                                              Structured logging
                                              (every request tracked)
```

**Step-by-step:**
1. A form is submitted by an end user.
2. Make.com's webhook module detects the new submission and sends a POST request to our FastAPI endpoint, with a shared-secret token in the header.
3. FastAPI validates the request: is the token correct? Is the payload shape correct (via Pydantic)? Has this exact `request_id` been seen before?
4. If valid and new, the form data is passed to the AI processing service, which asks Groq's Llama-3.3-70B model to summarize the submission and flag urgency.
5. The summary is posted to a Slack channel via an Incoming Webhook.
6. The API returns a structured response (`status`, `ai_summary`, `slack_posted`) — useful both for Make.com's own logging and for any future dashboard.
7. If any step fails, the failure is logged and reported to Slack as an alert, rather than disappearing silently.

---

## 3. Component Responsibilities

| Component | Responsibility | Why it's separated |
|---|---|---|
| `routes/webhook.py` | Orchestrates the request: auth → dedup → AI call → Slack call → response | Keeps HTTP concerns (status codes, request/response shape) separate from business logic |
| `services/ai_processor.py` | Talks to Groq, builds the prompt, returns a summary string | Can be swapped for a different LLM provider without touching the route |
| `services/slack_notifier.py` | Formats and sends the Slack message | Can be swapped for email/Notion/Teams without touching the AI logic |
| `core/security.py` | Verifies the shared-secret token | Auth logic isolated so it can be upgraded (e.g. to per-client tokens) without touching routes |
| `utils/idempotency.py` | Tracks seen `request_id`s | Isolated so the in-memory implementation can later be swapped for Redis without changing calling code |
| `core/logging_config.py` | Sets up structured logging | Centralized so log format is consistent across the whole app |

This separation is the difference between "a script that works" and "a service that can be maintained, extended, or handed off to another developer."

---

## 4. Key Design Decisions

### Why FastAPI over Flask
Native async support (needed for calling Slack/Groq without blocking), automatic request validation via Pydantic, and built-in OpenAPI docs — useful if this API is ever handed to another developer or integrated into a larger system.

### Why Groq instead of Gemini
Originally built against Gemini, but switched to Groq (Llama-3.3-70B) after hitting Gemini's free-tier rate limit mid-development. This turned out to be a reasonable default anyway — Groq's inference latency (observed ~2-3s in Day 26 benchmarking) is well suited to a "client watches the result appear in Slack live" demo.

### Why a shared-secret token instead of no auth
Without this, anyone who discovers the public ngrok/production URL could trigger the pipeline (spam Slack, burn API quota). A single shared secret is not enterprise-grade auth, but it's an appropriate amount of security for this stage of the project — documented here as a known simplification, not an oversight.

### Why idempotency matters here specifically
Automation platforms like Make.com sometimes retry webhook deliveries on timeout, even if the original request actually succeeded. Without a duplicate check, a single form submission could result in the same Slack alert being posted multiple times — confusing for the team on the receiving end. Tracking `request_id` prevents this.

### Why failures are reported to Slack, not just logged
If the AI call fails and the system only logs it to a file no one is watching, the client's team never finds out a submission was missed. Posting a visible failure alert to the same Slack channel keeps the failure from being invisible.

---

## 5. Known Simplifications (and what production would add)

| Current state | Production upgrade |
|---|---|
| Idempotency tracked in-memory (`set()`) | Redis or database-backed, so it survives restarts and scales across multiple server instances |
| Single shared secret token | Per-client API keys, or OAuth if integrating with multiple external platforms |
| Local + ngrok hosting | Persistent hosting (Railway, Render, Fly.io) with a stable public URL |
| No retry logic on transient failures | Retry with backoff for Groq/Slack calls (a transient Groq connection error was observed during related Day 26 work) |
| Logs to console only | Structured logs shipped to a log aggregator (e.g. Better Stack, Datadog) for production monitoring |

These are intentionally scoped out for this stage — the goal was to demonstrate the correct architecture and reasoning, not to over-engineer a demo project. Each of these is a natural "here's how I'd scale this for you" talking point in a client conversation.
# Day 19 — Agent Guardrails & Failure Mode Handling

Adding production-grade safety to AI agents: input validation, tool error recovery, infinite loop detection, and conversation-level flow control.

## What This Covers

- **Hallucination loop prevention** — agent stops acting on incorrect tool outputs
- **Tool misuse detection** — same-action repetition is caught and terminated
- **Infinite loop breaking** — hard iteration cap with graceful exit
- **Input validation** — harmful and toxic inputs blocked before reaching the LLM
- **NeMo Guardrails** — conversation-level flow control using Colang DSL
- **Adversarial testing** — agent tested against jailbreaks, toxic prompts, and edge cases

## Project Structure

```
day19/
├── guardrails_demo.py        # Input/output validation with Guardrails AI
├── guarded_react_agent.py    # ReAct agent with all 3 guardrail layers
├── nemo_demo/
│   ├── config/
│   │   ├── config.yml        # NeMo model and rails config
│   │   └── main.co           # Colang flow definitions
│   └── nemo_agent.py         # Conversation-level guardrails demo
└── README.md
```

## Guardrail Layers

### 1. Input Validation
Harmful, toxic, and adversarial inputs are blocked before the LLM call. Agent never processes malicious queries.

### 2. Tool Error Handling
Every tool is wrapped in try/except. Errors return structured error strings instead of crashing the agent. The agent reads the error and recovers gracefully.

### 3. Infinite Loop Detection
Two mechanisms running together:
- **Iteration cap** — hard stop at `MAX_ITERATIONS = 5`
- **Same-action detection** — if agent repeats the same tool call twice, loop is flagged and terminated

### 4. NeMo Guardrails (Conversation-Level)
Colang DSL defines explicit flows for:
- Jailbreak attempts (`ignore your instructions`, `DAN mode`)
- Harmful requests (`how to hack`, `how to hurt`)
- Safe topic enforcement

## Adversarial Test Results

| Input | Result |
|-------|--------|
| Normal math query | ✅ Answered correctly |
| Division by zero | ✅ Tool error caught, agent recovered |
| Toxic/harmful input | ❌ Blocked at input guard |
| Jailbreak attempt | ❌ Blocked by NeMo flow |
| Repeated same action | ⚠️ Loop detected, stopped gracefully |
| Max iterations hit | ⚠️ Hard stop with clear message |

## Tech Stack

- **LLM:** Gemini 2.5 Flash
- **Guardrails:** Guardrails AI + NeMo Guardrails
- **Agent Pattern:** ReAct (Reason + Act)
- **Package Manager:** uv
- **Language:** Python 3.11+

## Setup

```bash
uv add guardrails-ai nemoguardrails
guardrails hub install hub://guardrails/toxic_language
```

Add your Gemini API key to `.env`:
```
GEMINI_API_KEY=your_key_here
```

Run the guarded agent:
```bash
uv run guarded_react_agent.py
```

## Key Takeaway

A production AI agent must fail gracefully. This day covers the guardrail patterns that separate a demo project from a deployable product — input sanitization, tool resilience, and loop prevention working together as a single safety layer.

---

**80-Day AI Specialist Roadmap — Day 19/80**
GitHub: [github.com/Sameer-khaliq/Ai-Specialist](https://github.com/Sameer-khaliq/Ai-Specialist)
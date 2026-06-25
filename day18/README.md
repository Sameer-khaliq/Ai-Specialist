# Day 18 — Agent Memory Systems

Three-tier persistent memory agent built with mem0, ChromaDB, and Gemini 2.5 Flash.  
Tell it your name on turn 1 — it still knows on turn 20 after a full Python restart.

---

## What Was Built

A single `unified_chat()` function that combines three memory architectures simultaneously:

| Tier | Type | Storage | Survives Restart |
|------|------|---------|-----------------|
| Short-term | Conversation buffer | Python list (RAM) | ❌ No |
| Entity | Structured fact extraction | JSON file (SQLite-backed) | ✅ Yes |
| Long-term | Semantic vector search | ChromaDB via mem0 | ✅ Yes |

---

## Architecture

```
User Message
     │
     ▼
┌─────────────────────────────────────────┐
│  unified_chat()                         │
│                                         │
│  1. Extract entities → entity_store.json│
│  2. Semantic search → ChromaDB (mem0)   │
│  3. Build system prompt with context    │
│  4. Append last 10 messages (RAM)       │
│  5. Call Gemini 2.5 Flash               │
│  6. Write back → RAM + ChromaDB         │
└─────────────────────────────────────────┘
     │
     ▼
  Response
```

---

## How Each Memory Tier Works

### Short-term — Conversation Buffer
Plain Python list holding `HumanMessage` and `AIMessage` objects. Last 10 messages passed to Gemini each turn. Zero persistence — wiped when process exits. Fast, zero latency, no storage cost.

### Entity Memory — Structured JSON
On every user message, a separate Gemini call extracts structured key-value facts:
```
"My name is Sameer and I prefer FastAPI"
→ {"name": "Sameer", "preference": "FastAPI"}
```
Merges with existing `entity_store.json` so facts accumulate across turns. Injected into system prompt on every subsequent call.

### Long-term — Vector Store via mem0
Every full exchange (user message + AI response) gets embedded and stored in ChromaDB via mem0. On each new message, semantic search retrieves the most relevant past exchanges. Enables recall of context from weeks-old sessions based on meaning, not exact keywords.

---

## Restart Test Result

```
=== SESSION 1 ===
User:  My favorite stack is FastAPI + LangGraph. My dog's name is Max.
Agent: Got it, noted your stack and Max!

!!! PYTHON PROCESS KILLED — RAM WIPED !!!

=== SESSION 2 (fresh process) ===
User:  What's my favorite stack?
Agent: Your favorite stack is FastAPI + LangGraph.  ← from mem0/ChromaDB

User:  What's my dog's name?
Agent: Your dog's name is Max.  ← from mem0/ChromaDB
```

Both facts retrieved from persistent storage with zero RAM context. Test passed.

---

## Key Implementation Details

**Double LLM call per message:** Entity extraction uses a separate Gemini call before the main response. On the free tier (5 RPM), add `time.sleep(12)` between calls to avoid 429s.

**Graceful degradation:** Entity extraction wrapped in `try/except: pass` — if Gemini rate-limits the extraction call, the main chat continues unaffected. mem0 vector search still retrieves relevant context.

**USER_ID namespacing:** All mem0 memories scoped to `user_id="sameer_khaliq"`. In a multi-user product, this becomes dynamic per authenticated user — the architecture is already production-ready for that pattern.

**Hybrid search note:** ChromaDB supports semantic search only (no BM25 keyword search). For hybrid search, swap to Qdrant or pgvector as the mem0 backend.

---

## Files

```
day18/
├── memory_agent.py      # Core: unified_chat() with all 3 tiers
├── mem_config.py        # Local mem0 config pointing to ChromaDB
├── test_memory.py       # Restart test: Session 1 teach → kill → Session 2 recall
├── entity_store.json    # Auto-generated: persisted entity facts
└── README.md
```

---

## Stack

- `mem0ai` — memory orchestration layer
- `chromadb` — vector store for long-term semantic memory
- `langchain-google-genai` — Gemini 2.5 Flash LLM
- `langchain-core` — message types (HumanMessage, AIMessage, SystemMessage)
- `python-dotenv` — API key management

---

## Run

```powershell
uv add mem0ai langchain langchain-google-genai chromadb python-dotenv
uv run python day18/test_memory.py
```

---

## Concepts Learned

- Difference between session memory (RAM) and persistent memory (disk/vector store)
- Entity extraction via LLM as a standalone prompt pattern
- mem0 `memory.add()` and `memory.search()` API for semantic memory
- System prompt injection as the mechanism for long-term context delivery
- USER_ID-based memory namespacing for multi-user architecture
- Graceful degradation when one memory tier fails

---

*80-Day AI Specialist Roadmap — [github.com/Sameer-khaliq/Ai-Specialist](https://github.com/Sameer-khaliq/Ai-Specialist)*
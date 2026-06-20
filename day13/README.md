# Day 13 — Agentic RAG with ReAct

## Theory

Fixed RAG pipelines (Day 8-12) always retrieve, regardless of what the question
actually needs. That fails the moment queries stop being uniform — a math
question doesn't need document retrieval, and a "what's today's date" question
can't be answered from a static knowledge base at all.

**ReAct (Reason + Act)**, from the 2022 paper of the same name, fixes this by
making the LLM decide its own action sequence in a loop:

```
Thought: do I need a tool, and which one?
Action: call the chosen tool
Observation: read the result
Thought: do I have enough info, or do I need another tool?
... repeats until confident ...
Final Answer
```

This is the core mechanism behind every production AI agent that has to choose
*how* to answer, not just generate an answer.

## Architecture

```
User question
     │
     ▼
ReAct loop (Thought -> Action -> Observation, repeats)
     │
     ├── Calculator ────────────► math expression -> result
     ├── KnowledgeBaseRetriever ─► raw chunks from day12/chroma_db
     └── WebSearch (Tavily) ────► live web results
     │
     ▼
Final Answer
```

- `tools.py` — `Calculator` (safe math eval), `KnowledgeBaseRetriever` (raw
  top-k retrieval from the Day 12 ChromaDB collection, no per-chunk
  compression — the agent's own reasoning step does that filtering), and
  `WebSearch` (Tavily, live results).
- `agent.py` — `create_react_agent` (via `langchain_classic.agents`, after
  LangChain v1's restructuring moved it out of core `langchain.agents`) +
  `AgentExecutor`, model swappable between `gemini-2.5-flash` and
  `gemini-2.5-flash-lite` for quota management.
- `test_agent.py` — 15 queries across all 3 tool types, with a verification
  layer that checks the *actual observation text* for error markers
  (`ConnectionError`, etc.), not just whether the expected tool was called.
  This matters: a tool can be "selected correctly" but still fail silently if
  the agent falls back to internal knowledge instead of surfacing the failure.

## Results

**Tool selection accuracy: 15/15 (100%)**
**Tool selection + clean execution: 15/15 (100%)**

| Category | Queries | Tool selected correctly | Executed cleanly |
|---|---|---|---|
| Retrieval | 5 | 5/5 | 5/5 |
| Calculator | 5 | 5/5 | 5/5 |
| Web search | 5 | 5/5 | 5/5 |

### Notable trace — refusal instead of hallucination

Query: *"What is a hierarchical database model?"*

The knowledge base only covers centralized, client/server, and distributed
database types — not hierarchical models. Instead of generating a plausible
but fabricated answer, the agent retried the search once with a reworded
query, then explicitly reported the gap:

> "I am sorry, but the available knowledge base does not contain information
> regarding the hierarchical database model. It only provides information on
> centralized, client/server, and distributed database architectures."

This is the same principle validated by the Day 11 RAGAS faithfulness check —
a system that admits what it doesn't know is more trustworthy than one that
always produces a confident-sounding answer.

### Notable trace — correct tool routing under ambiguity

Query: *"What is 15 percent of 2400?"* required the agent to recognize a
percentage phrased in English needed translation into a Calculator-compatible
expression (`2400 * 0.15`) rather than treating it as a retrieval or search
query — correct on the first attempt.


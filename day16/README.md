# Day 16 — LangGraph Stateful Agent

## What this is
A multi-turn conversational agent that persists memory across server restarts 
using LangGraph's SqliteSaver checkpointer.

## Architecture
StateGraph → [add_message node] → [llm_call node] → conditional router
                                                          |
                                              SQLite (memory.db) reads/writes
                                              after every node step

## Why LangGraph over raw ReAct
- State management is declarative, not manual list appending
- Persistence is one line: `compile(checkpointer=saver)`
- Thread isolation built-in: each `thread_id` = separate user session
- Debuggable: `get_state_history()` shows every checkpoint

## The persistence proof
Run the agent, tell it your name. Kill the process. Run again with same 
thread_id. Ask "what's my name?" — it answers correctly from SQLite.

## How to run
```bash
uv run python agent.py
```

## Stack
- LangGraph 0.2+
- Gemini 2.5 Flash
- Gemini 2.5 Flash Lite
- SqliteSaver (local SQLite)
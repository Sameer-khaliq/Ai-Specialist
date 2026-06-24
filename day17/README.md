# Day 17 — CrewAI Multi-Agent Pipeline

## What this is
A 3-agent AI pipeline that takes any topic as input and autonomously 
produces a researched, written, and edited article — running completely 
free via Ollama locally (no API cost, no internet required).

## How it works
Topic input → Researcher Agent → Writer Agent → Editor Agent → Final article (.md)

Each agent is the same LLM (llama3) running with a different role, goal, 
and backstory. CrewAI handles the context passing between agents automatically.

## Agent breakdown
| Agent | Role | Tools |
|---|---|---|
| Researcher | Senior Research Analyst | DuckDuckGo search |
| Writer | Expert Content Writer | None |
| Editor | Chief Editor | None |

## Key concepts
- `Process.sequential` — agents run one after another, output flows forward
- `context=[prev_task]` — how one agent's output becomes next agent's input
- `backstory` — the system prompt that shapes each agent's behavior
- `max_iter` — limits LLM retry loops to prevent slow infinite loops

## Stack
- CrewAI
- Ollama + llama3 (local, free)
- LangChain Community (DuckDuckGo tool)

## How to run
```bash
# Start Ollama server first
ollama serve

# Run pipeline
uv run python main.py
# Enter any topic when prompted
```

## Sample output
Topic: "The Impact of Artificial Intelligence on Healthcare"  
Output: `output_The_Impact_of_Artificial_Intel.md`  
Editor score: 8.5/10

## vs Day 16 (LangGraph)
| | LangGraph | CrewAI |
|---|---|---|
| Control | Manual (you build the graph) | Automatic |
| Best for | Custom stateful flows | Role-based agent teams |
| Memory | SqliteSaver (explicit) | Built-in (optional) |
| Complexity | Higher | Lower |
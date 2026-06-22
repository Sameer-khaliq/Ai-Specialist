# Agent Architecture Failure Mode Analysis

**Benchmark Query:**
> "What is the current population of Pakistan? If it grows at 2.0% annually, what will it be in 5 years? Also find Pakistan's current literacy rate."

**Tools Available:** web_search, calculator

---

## Benchmark Results

| Metric                | ReAct | Reflexion | Plan-and-Execute |
|-----------------------|-------|-----------|-----------------|
| Population Found      |       |           |                 |
| Growth Calculated     |       |           |                 |
| Literacy Found        |       |           |                 |
| Completeness Score    |       |           |                 |
| Time (seconds)        |       |           |                 |
| LLM Calls (approx)    |       |           |                 |

---

## ReAct — Failure Mode Analysis

**Architecture:** Think → Act → Observe loop. No memory of mistakes.

**Observed Failures:**
-
-

**Root Cause:**
ReAct has no mechanism to evaluate its own output quality. Once it reaches a "Final Answer" step, it stops — even if the answer is incomplete. There is no retry or self-correction loop.

**When to use ReAct:**
- Simple, well-defined tasks
- Low latency requirement
- Single-hop reasoning

**When NOT to use ReAct:**
- Multi-part questions where partial answers are easy to miss
- Tasks requiring self-validation

---

## Reflexion — Failure Mode Analysis

**Architecture:** ReAct + Evaluator + Reflector. Self-corrects across multiple attempts.

**Observed Failures:**
-
-

**Root Cause:**
Reflection quality depends entirely on the evaluator prompt. A poorly scored output may trigger unnecessary retries (wasting API calls) or miss real failures. Also, on simple queries, Reflexion over-engineers the solution — 3 LLM calls where 1 would suffice.

**When to use Reflexion:**
- Hard tasks with verifiable outputs
- When accuracy matters more than speed
- When failure is expensive (e.g. writing code, financial calculations)

**When NOT to use Reflexion:**
- Simple lookups
- Latency-sensitive applications
- When API budget is tight

---

## Plan-and-Execute — Failure Mode Analysis

**Architecture:** Planner LLM creates full plan upfront → Executor runs step by step.

**Observed Failures:**
-
-

**Root Cause:**
The plan is static. If Step 1's web search returns unexpected data (e.g. population in a different unit, or outdated figures), Steps 2 and 3 use that bad data without any correction. The executor has no ability to replan mid-execution.

**When to use Plan-and-Execute:**
- Structured, predictable tasks
- Long multi-step workflows where order matters
- When you want transparency into what the agent will do before it does it

**When NOT to use Plan-and-Execute:**
- Dynamic tasks where results change the next step
- Tasks requiring adaptive decision-making

---

## Key Takeaways

1. **ReAct** is fastest but blind to its own mistakes
2. **Reflexion** is most accurate but expensive (3x LLM calls)
3. **Plan-and-Execute** is most transparent but most rigid

**Production recommendation:**
- Default: ReAct
- High-stakes tasks: Reflexion
- Long structured pipelines: Plan-and-Execute
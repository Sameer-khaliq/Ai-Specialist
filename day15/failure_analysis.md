# Agent Architecture Failure Mode Analysis

**Benchmark Query:**
> "What is the current population of Pakistan? If it grows at 2.0% annually, what will it be in 5 years? Also find Pakistan's current literacy rate."

**Tools Available:** web_search, calculator

---

## Benchmark Results

| Metric                | ReAct       | Reflexion    | Plan-and-Execute |
|-----------------------|-------------|--------------|-----------------|
| Population Found      | True        | True         |  True           |
| Growth Calculated     | True        | True         |  True           |
| Literacy Found        | True        | True         |  True           |
| Completeness Score    | 1.0         | 1.0          | 1.0             |
| Time (seconds)        | 34.9s       | 28.3s        | 18.2s           |
| LLM Calls (approx)    | ~3          | ~4           | ~3              |
| Reflexion Attempts    | N/A         | 1            | N/A             |

---

## ReAct — Failure Mode Analysis

**Architecture:** Think → Act → Observe loop. No memory of mistakes.

**Observed Failures:**
- Used 2023 population (247M) instead of most recent 2024 figure (251M) — picked older data from search results without verifying recency
- Literacy rate 58.86% pulled from 2021 data — no attempt to find a newer figure even though more recent data existed in search results

**Root Cause:**
ReAct has no mechanism to evaluate its own output quality. Once it reaches a "Final Answer" step, it stops — even if the answer used stale data. There is no retry or self-correction loop. It takes the first plausible number it sees.

**When to use ReAct:**
- Simple, well-defined tasks
- Low latency requirement
- Single-hop reasoning

**When NOT to use ReAct:**
- Multi-part questions where partial answers are easy to miss
- Tasks requiring self-validation or data recency verification

---

## Reflexion — Failure Mode Analysis

**Architecture:** ReAct + Evaluator + Reflector. Self-corrects across multiple attempts.

**Observed Failures:**
- Evaluator scored 0.5 on correct answers in earlier runs — the evaluator itself was unreliable, triggering unnecessary reflection loops
- 3 attempts were budgeted but only 1 was needed — reflection overhead adds latency even when the first answer is already good

**Root Cause:**
Reflection quality depends entirely on the evaluator prompt. A poorly calibrated evaluator may trigger unnecessary retries (wasting API calls) or miss real failures. On simple queries, Reflexion over-engineers the solution. In our run, it passed on attempt 1 with score 0.9, but earlier runs showed the evaluator giving 0.0 on perfectly correct answers — making the reflector useless.

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
- Step 3 calculator input was a literal variable name: `current_population_of_pakistan * (1.02**5)` — not an actual number. Calculator threw: `name 'current_population_of_pakistan' is not defined`
- Final answer compiler recovered independently by estimating — but the calculation was approximate and not verified, meaning a wrong answer was delivered confidently

**Root Cause:**
The planner created a static plan with a placeholder variable instead of a real number. The executor has no ability to replan mid-execution — when Step 3 failed, it just moved to Step 4 anyway. The compiler in Step 4 then fabricated a number without running an actual calculation. This is the most dangerous failure mode: **confident wrong answer with no error signal.**

**When to use Plan-and-Execute:**
- Structured, predictable tasks
- Long multi-step workflows where order matters
- When you want transparency into what the agent will do before it does it

**When NOT to use Plan-and-Execute:**
- Dynamic tasks where step results feed into next step inputs
- Tasks requiring adaptive decision-making mid-execution

---

## Key Takeaways

1. **ReAct** is fastest but blind to its own mistakes — uses stale data without noticing
2. **Reflexion** is most accurate but the evaluator itself can be wrong, causing wasted retries
3. **Plan-and-Execute** is most transparent but most rigid — a broken step silently produces a wrong answer

**Production recommendation:**
- Default: ReAct
- High-stakes tasks: Reflexion
- Long structured pipelines: Plan-and-Execute
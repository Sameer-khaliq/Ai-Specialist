# Day 23 — Prompt Optimization with DSPy

## Goal
Implement DSPy to auto-optimize prompts using labeled examples, and compare
DSPy-optimized vs hand-written prompts on a structured extraction task.

## Task
Extract `company`, `role`, and `salary_max` from messy, unstructured job
posting text (Slack messages, tweets, JSON blobs, legal-style postings, etc).

## Setup
- 12 labeled training examples (`trainset`) — used by the optimizer to select few-shot demos
- 12 held-out evaluation examples (`devset`) — never seen by the optimizer
- Model: Groq `llama-3.3-70b-versatile`
- Optimizer: `dspy.teleprompt.BootstrapFewShot` (max 4 bootstrapped demos)
- Module: `dspy.Predict` (chosen over `ChainOfThought` for a fair, token-matched
  comparison against the hand-written baseline)
- Metric: exact match (case/whitespace-insensitive) across all 3 fields

## Results

| Method | Devset Accuracy | Notes |
|---|---|---|
| Hand-written prompt | **100.00%** | explicit rules: digit-only salary, "k" conversion, exact "None" fallback |
| DSPy BootstrapFewShot (Predict) | **91.67%** (11/12) | auto-selected 4 few-shot demos from trainset; 1 failure on an all-caps "HUGGING FACE" posting |

## Key takeaway
The hand-written prompt won. This is a legitimate and useful finding, not a
failed experiment. DSPy's optimizer works by selecting which labeled examples
to inject as few-shot demonstrations — it does not rewrite instructions from
scratch. On a small, well-specified task like this one, with only 12 training
examples, a carefully hand-written prompt with explicit extraction rules can
match or beat an auto-optimized few-shot prompt.

DSPy's real advantage shows up on harder, more ambiguous tasks, multi-step
pipelines, or larger labeled datasets — not necessarily on narrow tasks where
a precise rule-based prompt is easy to write by hand.

## Bugs fixed during this experiment
- `lm.chat(...)` doesn't exist on `dspy.LM` — it's callable directly:
  `lm(prompt, max_tokens=200)`, returning a list of strings.
- `dspy.ChainOfThought` was initially used, which added a reasoning field and
  burned extra tokens, tripping Groq's free-tier TPM rate limit mid-evaluation
  and silently corrupting results as errors. Switched to `dspy.Predict` and
  added throttling (`time.sleep(1.5)`) between calls for a clean, fair run.
- File was originally named `dspy.py`, which shadowed the real `dspy` package
  on import. Renamed to `dspy_extraction.py`.

## Files
- `dspy_extraction.py` — full experiment: trainset, devset, baseline,
  DSPy program, optimizer, evaluation loop, comparison output
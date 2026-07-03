# Day 26 — Local LLM Deployment & Benchmarking (Local vs Cloud)

## Overview
Benchmarked local LLMs (via Ollama, running on CPU) against cloud APIs already in use (Groq, Gemini) across 5 tasks spanning easy to hard difficulty. Goal: build a data-backed decision framework for when local models are sufficient for a client's use case, and when cloud is worth the cost.

Note: GPT-3.5 was swapped for Groq (Llama-3.3-70B) and Gemini 2.5 Flash as the cloud baselines, since these are the APIs actually used in this project stack. This is arguably a more useful comparison for real client decisions — "local vs the cloud APIs you're already paying for."

## Models Tested
- **Local:** llama3.2 (2GB, via Ollama), mistral:7b (4.4GB, via Ollama) — both run on CPU, no GPU
- **Cloud:** Groq (llama-3.3-70b-versatile), Gemini 2.5 Flash

## Task Set
| Task | Difficulty | What it tests |
|---|---|---|
| Classification | Easy | Single-label categorization |
| Extraction | Easy | Structured field pulling from text |
| Summarization | Medium | Coherent 2-sentence compression |
| Math reasoning | Medium | Multi-step arithmetic |
| Code generation | Hard | Working Python function |

## Results

### Latency (avg seconds per response)
| Model | Avg Latency |
|---|---|
| Gemini 2.5 Flash | 5.51s |
| Groq Llama-3.3-70B | 2.80s |
| llama3.2 (local) | 124.44s |
| mistral:7b (local) | 255.47s |

Local models were **20-100x slower** than cloud APIs on this hardware (CPU-only, no GPU). This is the single biggest finding of the day.

### Accuracy (pass/fail on objective checks)
| Task | llama3.2 | mistral:7b | Groq | Gemini |
|---|---|---|---|---|
| Classification | PASS | PASS | PASS | PASS |
| Extraction | PASS | PASS | PASS | PASS |
| Math reasoning | PASS | **FAIL** | PASS | PASS |

Both local and cloud models handled classification and extraction perfectly. On math reasoning, llama3.2 succeeded but mistral:7b made an arithmetic error in the final step, despite showing correct intermediate steps.

### Summarization & Code Generation (manual review)
- **Summarization:** llama3.2, mistral:7b, and Gemini all produced coherent, accurate 2-sentence summaries. Groq errored on this call (transient connection error, not a model limitation — worth a retry in a production setup).
- **Code generation:** All models produced a correct `is_palindrome()` function using the same core logic (strip non-alphanumeric chars, lowercase, compare to reverse). No functional differences between local and cloud on this task.

## Key Finding: When Local Is Sufficient

**Local models are a good fit when:**
- The task is simple and well-defined (classification, extraction, template filling)
- Latency isn't critical — batch/offline processing rather than real-time user-facing chat
- Data privacy matters more than speed (data never leaves the client's machine)
- Call volume is high enough that cloud API costs would add up, and the client has decent hardware (ideally GPU — this test was CPU-only, worst case)

**Cloud is worth the cost when:**
- Multi-step reasoning or math is involved (mistral:7b's failure here is a real risk in production)
- Response speed matters (cloud was 20-100x faster in this test)
- The task needs a bigger model's broader capability (code gen, nuanced summarization)
- The client doesn't have spare compute/RAM to dedicate to a local model

**Practical recommendation:** For most freelance client use cases — simple classification/extraction pipelines run in the background — local models are viable and save real money. For anything user-facing, reasoning-heavy, or latency-sensitive, cloud APIs (especially Groq, which was both fast and accurate here) are the safer default.

## Known Issue
One Groq call (t3 summarization) failed with a transient connection error. Did not block the rest of the benchmark; worth adding retry logic in a production version of this pipeline.

## How to Run
```
uv run day26/benchmark.py
```
Outputs `results.csv` with per-task, per-model latency and pass/fail data.
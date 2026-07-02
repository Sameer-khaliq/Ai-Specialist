# benchmark.py
import pandas as pd
from task import TASKS
from runners import run_ollama, run_groq, run_gemini

MODELS = [
    ("mistral:7b", "local"),
    ("llama3:8b", "local"),
    ("groq-llama3.3-70b", "cloud"),
    ("gemini-2.5-flash", "cloud"),
]

results = []

for task in TASKS:
    for model_name, kind in MODELS:
        if model_name == "groq-llama3.3-70b":
            output, latency = run_groq(task["prompt"])
        elif model_name == "gemini-2.5-flash":
            output, latency = run_gemini(task["prompt"])
        else:
            output, latency = run_ollama(model_name, task["prompt"])

        results.append({
            "task_id": task["id"],
            "difficulty": task["difficulty"],
            "model": model_name,
            "kind": kind,
            "latency_sec": round(latency, 2),
            "output": output[:200],  
        })
        print(f"{task['id']} | {model_name} | {latency:.2f}s")

df = pd.DataFrame(results)
df.to_csv("results.csv", index=False)
print("\nSaved to results.csv")
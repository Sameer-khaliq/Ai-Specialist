import pandas as pd
from dotenv import load_dotenv
from task import TASKS
from runners import run_ollama, run_groq, run_gemini
load_dotenv()

MODELS = [
    ("llama3.2", "local"),
    ("mistral:7b", "local"),
    ("groq-llama3.3-70b", "cloud"),
    ("gemini-2.5-flash", "cloud"),
]


def check_t1(output: str) -> bool:
    return "complaint" in output.lower()


def check_t2(output: str) -> bool:
    return "john carter" in output.lower() and "450" in output


def check_t4(output: str) -> bool:
    # 120 * 0.65 = 78, 78 * 0.8 = 62.4 -> 62 remain
    return "62" in output


CHECKS = {
    "t1_classification": check_t1,
    "t2_extraction": check_t2,
    "t4_reasoning": check_t4,
}


def run_model(model_name: str, prompt: str):
    if model_name == "groq-llama3.3-70b":
        return run_groq(prompt)
    elif model_name == "gemini-2.5-flash":
        return run_gemini(prompt)
    else:
        return run_ollama(model_name, prompt)


def main():
    results = []

    for task in TASKS:
        for model_name, kind in MODELS:
            try:
                output, latency = run_model(model_name, task["prompt"])
            except Exception as e:
                output, latency = f"ERROR: {e}", None

            check_fn = CHECKS.get(task["id"])
            passed = check_fn(output) if check_fn and isinstance(output, str) else None

            results.append({
                "task_id": task["id"],
                "difficulty": task["difficulty"],
                "model": model_name,
                "kind": kind,
                "latency_sec": round(latency, 2) if latency else None,
                "passed_check": passed,
                "output": output[:200].replace("\n", " "),
            })

            print(f"{task['id']:22} | {model_name:20} | "
                  f"{f'{latency:.2f}s' if latency else 'ERR':>7} | "
                  f"{'PASS' if passed else ('N/A' if passed is None else 'FAIL')}")

    df = pd.DataFrame(results)
    df.to_csv("results.csv", index=False)
    print("\nSaved to results.csv")

    print("\n--- Avg latency by model ---")
    print(df.groupby("model")["latency_sec"].mean().round(2))


if __name__ == "__main__":
    main()
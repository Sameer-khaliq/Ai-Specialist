import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langsmith import Client

load_dotenv(r"C:\ai-specialist\.env")

client = Client()
PROJECT_NAME = "day22"


def get_run_stats(hours_back: int = 24):
    runs = list(client.list_runs(
        project_name=PROJECT_NAME,
        start_time=datetime.now() - timedelta(hours=hours_back),
    ))

    if not runs:
        print(f"No runs found in '{PROJECT_NAME}' in the last {hours_back}h.")
        return

    total_tokens = 0
    total_latency = 0.0
    total_cost = 0.0
    latency_count = 0
    by_name = {}

    for run in runs:
        name = run.name or "unknown"
        by_name.setdefault(name, {"count": 0, "tokens": 0, "latency": 0.0})
        by_name[name]["count"] += 1

        if run.total_tokens:
            total_tokens += run.total_tokens
            by_name[name]["tokens"] += run.total_tokens

        if run.total_cost:
            total_cost += float(run.total_cost)

        if run.end_time and run.start_time:
            latency = (run.end_time - run.start_time).total_seconds()
            total_latency += latency
            latency_count += 1
            by_name[name]["latency"] += latency

    print(f"\n{'='*50}")
    print(f"LangSmith Stats — project: {PROJECT_NAME}")
    print(f"Window: last {hours_back}h")
    print(f"{'='*50}")
    print(f"Total runs:      {len(runs)}")
    print(f"Total tokens:    {total_tokens}")
    print(f"Total cost:      ${total_cost:.4f}")
    if latency_count:
        print(f"Avg latency:     {total_latency/latency_count:.2f}s")
        print(f"Total latency:   {total_latency:.2f}s")

    print(f"\n{'Per-node breakdown':-^50}")
    for name, stats in sorted(by_name.items(), key=lambda x: -x[1]["count"]):
        avg_lat = stats["latency"] / stats["count"] if stats["count"] else 0
        print(f"  {name:25} runs={stats['count']:3}  tokens={stats['tokens']:6}  avg_latency={avg_lat:.2f}s")

    print(f"{'='*50}\n")


if __name__ == "__main__":
    get_run_stats(hours_back=24)

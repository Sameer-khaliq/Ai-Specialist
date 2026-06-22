import json
import time
from react_agent import run_react_agent
from reflexion_agent import run_reflexion_agent
from plan_execute_agent import run_plan_execute_agent

# ── Benchmark Query ────────────────────────────────────────────────────────────
BENCHMARK_QUERY = (
    "What is the current population of Pakistan? "
    "If it grows at 2.0% annually, what will it be in 5 years? "
    "Also find Pakistan's current literacy rate."
)

# ── Scoring helper ─────────────────────────────────────────────────────────────
def score_result(result: dict) -> dict:
    output = result.get("output", "").lower()

    population_found  = any(w in output for w in ["million", "billion", "population", "230", "231", "232", "233", "240", "250", "251", "259"])
    growth_calculated = any(w in output for w in ["5 year", "five year", "2029", "2030", "2031", "254", "255", "256", "253", "260", "277", "286"])
    literacy_found    = any(w in output for w in ["literacy", "literate", "58", "60", "62", "63", "%"])

    score = sum([population_found, growth_calculated, literacy_found]) / 3

    return {
        "population_found":  population_found,
        "growth_calculated": growth_calculated,
        "literacy_found":    literacy_found,
        "completeness_score": round(score, 2),
    }

# ── Run all agents ─────────────────────────────────────────────────────────────
def run_benchmark():
    print("\n" + "="*60)
    print("BENCHMARK: Running all 3 agents on same query")
    print(f"Query: {BENCHMARK_QUERY}")
    print("="*60)

    results = {}

    # 1. ReAct
    print("\n\n>>> AGENT 1: ReAct")
    t0 = time.time()
    react_result = run_react_agent(BENCHMARK_QUERY)
    react_result["time_seconds"] = round(time.time() - t0, 1)
    react_result["scores"] = score_result(react_result)
    results["ReAct"] = react_result

    # 2. Reflexion
    print("\nWaiting 30s before next agent...")
    time.sleep(30)
    print("\n\n>>> AGENT 2: Reflexion")
    t0 = time.time()
    reflexion_result = run_reflexion_agent(BENCHMARK_QUERY, max_attempts=3, pass_threshold=0.85)
    reflexion_result["time_seconds"] = round(time.time() - t0, 1)
    reflexion_result["scores"] = score_result(reflexion_result)
    results["Reflexion"] = reflexion_result

    # 3. Plan-and-Execute
    print("\nWaiting 30s before next agent...")
    time.sleep(30)
    print("\n\n>>> AGENT 3: Plan-and-Execute")
    t0 = time.time()
    plan_result = run_plan_execute_agent(BENCHMARK_QUERY)
    plan_result["time_seconds"] = round(time.time() - t0, 1)
    plan_result["scores"] = score_result(plan_result)
    results["PlanExecute"] = plan_result

    # ── Summary Table ──────────────────────────────────────────────────────────
    print("\n\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    print(f"{'Metric':<30} {'ReAct':>10} {'Reflexion':>12} {'PlanExec':>10}")
    print("-"*65)

    for metric in ["population_found", "growth_calculated", "literacy_found", "completeness_score"]:
        r  = results["ReAct"]["scores"][metric]
        rf = results["Reflexion"]["scores"][metric]
        pe = results["PlanExecute"]["scores"][metric]
        print(f"{metric:<30} {str(r):>10} {str(rf):>12} {str(pe):>10}")

    print("-"*65)
    print(f"{'Time (seconds)':<30} {results['ReAct']['time_seconds']:>10} {results['Reflexion']['time_seconds']:>12} {results['PlanExecute']['time_seconds']:>10}")

    # Reflexion-specific
    if "total_attempts" in results["Reflexion"]:
        print(f"{'Reflexion attempts':<30} {'N/A':>10} {results['Reflexion']['total_attempts']:>12} {'N/A':>10}")

    print("\n\nFINAL OUTPUTS:")
    for agent_name, r in results.items():
        print(f"\n[{agent_name}]\n{r['output']}\n")

    # Save results to JSON
    with open("benchmark_results.json", "w") as f:
        # make serializable
        for k in results:
            results[k].pop("attempt_log", None)
        json.dump(results, f, indent=2)
    print("\nResults saved to benchmark_results.json")

    return results

if __name__ == "__main__":
    run_benchmark()
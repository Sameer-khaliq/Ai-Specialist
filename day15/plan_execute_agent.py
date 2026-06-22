import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

load_dotenv()

# ── LLM ───────────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

# ── Tools ─────────────────────────────────────────────────────────────────────
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(round(result, 2))
    except Exception as e:
        return f"Calculator error: {e}"

tavily = TavilySearchResults(
    max_results=2,
    api_key=os.getenv("TAVILY_API_KEY"),
)

# Tool dispatcher — executor uses this
def dispatch_tool(tool_name: str, tool_input: str) -> str:
    if tool_name == "web_search":
        results = tavily.invoke(tool_input)
        if isinstance(results, list):
            return "\n".join([r.get("content", "") for r in results[:2]])
        return str(results)
    elif tool_name == "calculator":
        return calculator.invoke(tool_input)
    else:
        return f"Unknown tool: {tool_name}"

# ── PLANNER — creates a step-by-step plan ─────────────────────────────────────
def plan(query: str) -> list[dict]:
    planner_prompt = f"""You are a planner. Break down this question into clear sequential steps.

    Question: {query}

    Available tools:
    - web_search: Search the internet for real-time information
    - calculator: Evaluate math expressions like '230000000 * (1.02 ** 5)'
    - final_answer: Compile all results into a final answer

    Return a JSON array of steps. Each step must have:
    - "step_num": integer
    - "description": what this step does
    - "tool": one of [web_search, calculator, final_answer]
    - "tool_input": exact input to pass to the tool

    Return ONLY valid JSON array, nothing else. Example:
    [
    {{"step_num": 1, "description": "Search for X", "tool": "web_search", "tool_input": "X 2024"}},
    {{"step_num": 2, "description": "Calculate Y", "tool": "calculator", "tool_input": "100 * 1.02"}},
    {{"step_num": 3, "description": "Compile answer", "tool": "final_answer", "tool_input": "Summarize all results"}}
    ]"""

    response = llm.invoke(planner_prompt)
    
    # Check if response is a message object or dictionary
    if hasattr(response, 'content'):
        res_text = response.content
    elif isinstance(response, dict):
        res_text = response.get('content', str(response))
    else:
        res_text = str(response)

    # Safeguard against list or structural types
    if isinstance(res_text, list):
        raw = " ".join([str(x) for x in res_text]).strip()
    else:
        raw = str(res_text).strip()

    # strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        steps = json.loads(raw)
        return steps
    except json.JSONDecodeError:
        print(f"[PLANNER] Failed to parse plan JSON:\n{raw}")
        return []

# ── EXECUTOR — runs each step ──────────────────────────────────────────────────
def execute_steps(steps: list[dict]) -> list[dict]:
    results = []
    context = {}  # accumulated results from previous steps

    for step in steps:
        step_num = step.get("step_num")
        tool_name = step.get("tool")
        tool_input = step.get("tool_input", "")
        description = step.get("description", "")

        print(f"\n[EXECUTOR] Step {step_num}: {description}")
        print(f"  Tool: {tool_name} | Input: {tool_input}")

        if tool_name == "final_answer":
            # Compile all previous results
            compiler_prompt = f"""You are compiling a final answer.

                                Original question: {context.get('query', '')}

                                Results collected:
                                {json.dumps(results, indent=2)}

                                Write a clear, complete final answer using these results."""
            response = llm.invoke(compiler_prompt)
            output = response.content.strip()
        else:
            output = dispatch_tool(tool_name, tool_input)

        print(f"  Result: {output[:200]}...")

        results.append({
            "step_num": step_num,
            "tool": tool_name,
            "input": tool_input,
            "output": output,
        })
        context[f"step_{step_num}"] = output

    return results

# ── Main Plan-and-Execute Runner ───────────────────────────────────────────────
def run_plan_execute_agent(query: str) -> dict:
    print(f"\n{'='*60}")
    print("PLAN-AND-EXECUTE AGENT STARTING")
    print(f"{'='*60}")

    # Step 1: Plan
    print("\n[PLANNER] Creating plan...")
    steps = plan(query)

    if not steps:
        return {
            "agent": "Plan-and-Execute",
            "query": query,
            "error": "Planner failed to generate steps",
            "output": "Failed",
        }

    print(f"\n[PLANNER] Plan created — {len(steps)} steps:")
    for s in steps:
        print(f"  Step {s['step_num']}: {s['description']} [{s['tool']}]")

    # Step 2: Execute
    results = execute_steps(steps)

    # Final output is last step's output
    final_output = results[-1]["output"] if results else "No output"

    return {
        "agent": "Plan-and-Execute",
        "query": query,
        "plan": steps,
        "execution_results": results,
        "total_steps": len(steps),
        "output": final_output,
    }

if __name__ == "__main__":
    from benchmark_task import BENCHMARK_QUERY
    result = run_plan_execute_agent(BENCHMARK_QUERY)
    print("\n" + "="*60)
    print(f"AGENT: {result['agent']}")
    print(f"TOTAL STEPS: {result['total_steps']}")
    print(f"FINAL OUTPUT:\n{result['output']}")
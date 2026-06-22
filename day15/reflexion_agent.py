import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import AgentExecutor, create_react_agent

load_dotenv()

# ── LLM ───────────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

# ── Tools ─────────────────────────────────────────────────────────────────────
@tool(description="Evaluate a mathematical expression. Input must be a valid Python math expression. Example: '1000000 * (1.02 ** 5)'")
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(round(result, 2))
    except Exception as e:
        return f"Calculator error: {e}"

web_search = TavilySearchResults(
    max_results=2,
    api_key=os.getenv("TAVILY_API_KEY"),
)
web_search.name = "web_search"
web_search.description = "Search the web for current real-world information like population, GDP, literacy rates, etc."

tools = [web_search, calculator]
template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

# ── Evaluator — scores the output 0.0 to 1.0 ──────────────────────────────────
def evaluate_output(query: str, output: str) -> float:
    eval_prompt = f"""You are evaluating an AI agent's answer.

Question: {query}
Answer: {output}

Score this answer from 0.0 to 1.0 based on:
- Did it answer ALL parts of the question? (0.4 points)
- Did it use real searched data, not made-up numbers? (0.3 points)  
- Is the calculation correct and shown? (0.3 points)

Reply with ONLY a decimal number like 0.7 or 1.0. Nothing else."""

    response = llm.invoke(eval_prompt)
    try:
        score = float(response.content.strip())
        return min(max(score, 0.0), 1.0)  # clamp between 0 and 1
    except:
        return 0.5  # default if parsing fails

# ── Reflector — writes what went wrong ────────────────────────────────────────
def reflect_on_failure(query: str, output: str, score: float, prev_reflections: list) -> str:
    prev_text = "\n".join(prev_reflections) if prev_reflections else "None"
    reflect_prompt = f"""You are helping an AI agent improve its answers.

Question: {query}
Previous reflections: {prev_text}
Latest answer: {output}
Score: {score}/1.0

Write a SHORT reflection (2-3 sentences) on:
1. What was missing or wrong in this answer?
2. What should the agent do differently next time?"""

    response = llm.invoke(reflect_prompt)
    return response.content.strip()

# ── Actor — ReAct agent with reflection context ────────────────────────────────
def run_actor(query: str, reflections: list) -> str:
    reflection_context = ""
    if reflections:
        reflection_context = "\n\nPrevious attempt reflections (learn from these):\n"
        for i, r in enumerate(reflections, 1):
            reflection_context += f"Attempt {i}: {r}\n"

    enriched_query = query + reflection_context

    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=12,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
    result = executor.invoke({"input": enriched_query})
    output = result.get("output", "")
    if not output or "agent stopped" in output.lower():
        steps = result.get("intermediate_steps", [])
        if steps:
            output = f"Based on research: {str(steps[-1][1])}"
    return output

# ── Main Reflexion Loop ────────────────────────────────────────────────────────
def run_reflexion_agent(query: str, max_attempts: int = 3, pass_threshold: float = 0.85) -> dict:
    reflections = []
    attempt_log = []

    print(f"\n{'='*60}")
    print("REFLEXION AGENT STARTING")
    print(f"{'='*60}")

    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Attempt {attempt}/{max_attempts} ---")

        # Actor runs
        output = run_actor(query, reflections)

        # Evaluator scores
        score = evaluate_output(query, output)
        print(f"\n[EVALUATOR] Score: {score}")

        attempt_log.append({
            "attempt": attempt,
            "output": output,
            "score": score,
        })

        # Pass threshold reached
        if score >= pass_threshold:
            print(f"[REFLEXION] Passed threshold ({score} >= {pass_threshold}). Done!")
            break

        # Reflector writes what went wrong
        if attempt < max_attempts:
            reflection = reflect_on_failure(query, output, score, reflections)
            reflections.append(reflection)
            print(f"[REFLECTOR] {reflection}")

    best = max(attempt_log, key=lambda x: x["score"])

    return {
        "agent": "Reflexion",
        "query": query,
        "total_attempts": len(attempt_log),
        "reflections": reflections,
        "attempt_log": attempt_log,
        "best_score": best["score"],
        "output": best["output"],
    }

if __name__ == "__main__":
    from benchmark_task import BENCHMARK_QUERY
    result = run_reflexion_agent(BENCHMARK_QUERY)
    print("\n" + "="*60)
    print(f"AGENT: {result['agent']}")
    print(f"TOTAL ATTEMPTS: {result['total_attempts']}")
    print(f"BEST SCORE: {result['best_score']}")
    print(f"FINAL OUTPUT:\n{result['output']}")
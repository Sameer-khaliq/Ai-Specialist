import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_experimental.tools import PythonREPLTool

load_dotenv()

# ── 1. LLM ──────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,  # 0 = deterministic, we want consistent code not creative
)

# ── 2. Tool ─────────────────────────────────────────────────────────────────
# PythonREPLTool runs code locally via exec()
# WARNING: only use for learning — unsafe for production
python_repl = PythonREPLTool()

tools = [python_repl]

# ── 3. Prompt ────────────────────────────────────────────────────────────────
# ReAct format: Thought → Action → Observation → loop → Final Answer
# We explicitly tell the agent to self-debug
prompt = PromptTemplate.from_template("""
You are an expert Python developer and autonomous coding agent.

Your job:
1. Receive a coding task in plain English
2. Write clean Python code to solve it
3. Execute the code using the python_repl tool
4. If there's an error, READ the error carefully, FIX the code, and try again
5. Keep trying until the code works (max 5 attempts)
6. Return the final working result

IMPORTANT RULES:
- Always use print() to display results — otherwise you won't see them
- When you get an error, show the fixed code and explain what was wrong
- Be systematic: one fix at a time

You have access to these tools:
{tools}

Tool names: {tool_names}

Use this EXACT format:

Question: the coding task you must solve
Thought: what you plan to do
Action: the tool name (must be one of {tool_names})
Action Input: the Python code to execute
Observation: the result from the tool
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now have the final answer
Final Answer: the result + explanation of what the code does

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")

# ── 4. Agent ─────────────────────────────────────────────────────────────────
# create_react_agent builds a ReAct agent (Reason + Act loop)
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

# AgentExecutor is the runtime — it drives the Thought→Action→Observation loop
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,        # shows every step — KEEP THIS ON so you can learn
    max_iterations=10,   # prevents infinite loops
    handle_parsing_errors=True,  # if LLM formats output wrong, retry
)

# ── 5. Test Tasks ─────────────────────────────────────────────────────────────
def run_task(task: str):
    print(f"\n{'='*60}")
    print(f"TASK: {task}")
    print('='*60)
    result = agent_executor.invoke({"input": task})
    print(f"\nFINAL RESULT:\n{result['output']}")
    return result

if __name__ == "__main__":
    # Task 1: Simple computation
    run_task("Calculate the first 10 Fibonacci numbers and print them")

    # Task 2: This will likely cause an error on first try (intentional)
    # The agent must catch it and fix it
    run_task(
        "Create a list of 5 random numbers between 1 and 100, "
        "sort them, and print the median. Use only built-in Python — no numpy."
    )

    # Task 3: File operation
    run_task(
        "Write a Python function that checks if a string is a palindrome. "
        "Test it with: 'racecar', 'hello', 'madam'. Print True/False for each."
    )
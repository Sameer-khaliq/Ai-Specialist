import os
import sys
import io
import traceback
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

call_count = 0

def execute_locally(code: str) -> str:
    """Run code locally using exec() — captures stdout, stderr, and exceptions."""
    global call_count
    call_count += 1
    print(f"\n[Attempt #{call_count}] Running locally...")

    # Redirect stdout so we can capture print() output
    stdout_capture = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout_capture

    try:
        exec(code, {})  # empty dict = clean namespace each run
        output = stdout_capture.getvalue()
        return f"STDOUT:\n{output}" if output else "Executed (no output)"
    except Exception as e:
        output = stdout_capture.getvalue()
        tb = traceback.format_exc()
        result = ""
        if output:
            result += f"STDOUT (before error):\n{output}\n\n"
        result += f"ERROR: {type(e).__name__}: {e}\nTraceback:\n{tb}"
        return result
    finally:
        sys.stdout = old_stdout  # always restore stdout


sandbox_tool = Tool(
    name="python_sandbox",
    description="Run Python code locally. Returns stdout/stderr/errors.",
    func=execute_locally,
)

prompt = PromptTemplate.from_template("""
You are an autonomous debugging agent. You write code, run it, fix errors, repeat.
Never give up on first error — always read the traceback and fix it.

Tools: {tools}
Tool names: {tool_names}

Format:
Question: {input}
Thought: {agent_scratchpad}
Action: python_sandbox
Action Input: <code>
Observation: <result>
...
Final Answer: <working result>
""")

agent = create_react_agent(llm=llm, tools=[sandbox_tool], prompt=prompt)
executor = AgentExecutor(
    agent=agent,
    tools=[sandbox_tool],
    verbose=True,
    max_iterations=20,
    handle_parsing_errors=True,
)

HARD_TASKS = [
    "Calculate the average of an empty list safely — "
    "handle the ZeroDivisionError and print 'No data' if the list is empty. "
    "Test with: [] and [10, 20, 30].",

    "Write a recursive function to compute factorial of n. "
    "Test with n=0, 1, 5, 10. Print each result. "
    "Make sure it handles n=0 correctly (should be 1).",

    "From this sentence: 'banana apple cherry apple banana banana cherry mango', "
    "build a dict of word counts, then print only words that appear more than once, "
    "sorted alphabetically.",
]

for task in HARD_TASKS:
    call_count = 0
    print(f"\n{'='*30}")
    result = executor.invoke({"input": task})
    print(f"\nDone in {call_count} sandbox call(s)")
    print(f"ANSWER: {result['output']}")
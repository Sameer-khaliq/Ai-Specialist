import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from e2b_code_interpreter import Sandbox

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Track how many sandbox calls happen (shows retry behavior)
call_count = 0

def execute_and_track(code: str) -> str:
    global call_count
    call_count += 1
    print(f"\n [Attempt #{call_count}] Running in E2B sandbox...")

    with Sandbox() as sandbox:
        execution = sandbox.run_code(code)
        parts = []

        if execution.logs.stdout:
            parts.append("STDOUT:\n" + "\n".join(execution.logs.stdout))
        if execution.logs.stderr:
            parts.append("STDERR:\n" + "\n".join(execution.logs.stderr))
        if execution.error:
            parts.append(
                f"ERROR: {execution.error.name}: {execution.error.value}\n"
                f"Traceback: {execution.error.traceback}"
            )
        if not parts:
            return "Executed (no output)"
        return "\n\n".join(parts)

sandbox_tool = Tool(
    name="python_sandbox",
    description="Run Python code in a secure sandbox. Returns stdout/stderr/errors.",
    func=execute_and_track,
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

# ── Challenging tasks designed to provoke at least one debug cycle ────────────
HARD_TASKS = [
    # This requires understanding that division of ints gives float in Python 3
    # LLM might forget to handle edge cases
    "Calculate the average of an empty list safely — "
    "handle the ZeroDivisionError and print 'No data' if the list is empty. "
    "Test with: [] and [10, 20, 30].",

    # Requires correct recursion with base case
    "Write a recursive function to compute factorial of n. "
    "Test with n=0, 1, 5, 10. Print each result. "
    "Make sure it handles n=0 correctly (should be 1).",

    # Requires correct use of dict comprehension and sorting
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
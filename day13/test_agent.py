# day13/test_agent.py

from agent import build_agent

TEST_QUERIES = [
    ("What is a centralized database?", "KnowledgeBaseRetriever"),
    ("What are the types of computers based on size?", "KnowledgeBaseRetriever"),
    ("Explain client/server database architecture.", "KnowledgeBaseRetriever"),
    ("What is a microcomputer?", "KnowledgeBaseRetriever"),
    ("What is a hierarchical database model?", "KnowledgeBaseRetriever"),
    ("What is 847 * 23?", "Calculator"),
    ("Calculate the square root of 1764.", "Calculator"),
    ("What is 15 percent of 2400?", "Calculator"),
    ("What is (45 + 78) / 3?", "Calculator"),
    ("Calculate 2 to the power of 10.", "Calculator"),
    ("What is today's date?", "WebSearch"),
    ("Who is the current CEO of OpenAI?", "WebSearch"),
    ("What is the latest stable version of Python?", "WebSearch"),
    ("What is the current price of Bitcoin in USD?", "WebSearch"),
    ("What is the weather like in Lahore right now?", "WebSearch"),
]

ERROR_MARKERS = ["ConnectionError", "Error evaluating", "No relevant information", "Traceback"]


def observation_failed(observation) -> bool:
    """Check the actual tool output text for error signatures — not just whether the tool was called."""
    text = str(observation)
    return any(marker in text for marker in ERROR_MARKERS)


def run_test():
    executor = build_agent(model_name="gemini-3.1-flash-lite", return_intermediate_steps=True)
    tool_correct = 0
    tool_and_execution_correct = 0

    for query, expected_tool in TEST_QUERIES:
        result = executor.invoke({"input": query})
        steps = result.get("intermediate_steps", [])
        tools_used = [action.tool for action, _ in steps]

        tool_match = expected_tool in tools_used

        tool_succeeded = False
        for action, observation in steps:
            if action.tool == expected_tool and not observation_failed(observation):
                tool_succeeded = True
                break

        if tool_match:
            tool_correct += 1
        if tool_match and tool_succeeded:
            tool_and_execution_correct += 1

        status = "PASS" if (tool_match and tool_succeeded) else "FAIL"
        print(f"Query: {query}")
        print(f"  Expected: {expected_tool} | Used: {tools_used} | "
              f"selected_correctly={tool_match} | executed_cleanly={tool_succeeded} | {status}")
        print(f"  Answer: {result['output']}\n")

    n = len(TEST_QUERIES)
    print(f"Tool SELECTION accuracy: {tool_correct}/{n} ({round(100*tool_correct/n,1)}%)")
    print(f"Tool selection AND clean execution: {tool_and_execution_correct}/{n} "
          f"({round(100*tool_and_execution_correct/n,1)}%)")


if __name__ == "__main__":
    run_test()
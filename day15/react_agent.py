import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import AgentExecutor, create_react_agent
 
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash",
    google_api_key = os.getenv("GEMINI_API_KEY")
)

#_____________TOOLS____________________
@tool(description="Evaluate a mathematical expression. Input must be a valid Python math expression. Example: '1000000 * (1.02 ** 5)'")

def calculator(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__":{}}, {})
        return str(round(result,2))
    except Exception as e:
        print(f"Calculation error: {e}")


web_search = TavilySearchResults(
    max_results = 2,
    api_key = os.getenv("TAVILY_API_KEY")
)
web_search.name = "web_search"
web_search.description = "Search the web for current real-world information like population, GDP, literacy rates, etc."

tools = [calculator, web_search]



#___Prompt____
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

#______agent____

def run_react_agent(query:str)->dict:
    agent = create_react_agent(llm , tools, prompt)
    executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=15,  
            handle_parsing_errors=True,
        )
    try:
        result = executor.invoke({"input": query})
        output = result.get("output", "No response extracted.")
    except Exception as e:
        output = f"Agent execution stopped or failed. Error: {e}"

    return {
        "agent": "ReAct",
        "query": query,
        "output": output,
    }
if __name__ == "__main__":
    from benchmark_task import BENCHMARK_QUERY
    result = run_react_agent(BENCHMARK_QUERY)
    print("\n" + "="*60)
    print(f"AGENT: {result['agent']}")
    print(f"OUTPUT:\n{result['output']}")
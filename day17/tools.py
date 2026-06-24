from crewai_tools import SerperDevTool
from langchain_community.tools import DuckDuckGoSearchRun

def get_search_tool():
    try:
        tool = DuckDuckGoSearchRun()
        return tool
    except Exception:
        import os
        if os.getenv("SERPER_API_KEY"):
            return SerperDevTool()
        else:
            print("WARNING: No search tool available. Researcher will use LLM knowledge only.")
            return None
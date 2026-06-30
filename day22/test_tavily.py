import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv(r"C:\ai-specialist\.env")

tavily_search = TavilySearch(
    max_results=5,
    search_depth="basic",
    include_raw_content=False,
)

queries = [
    "Future of freelancing in artificial intelligence 2026",
    "Emerging trends in AI agent freelancing market",
    "AI powered freelance workforce opportunities and challenges 2026",
]

for query in queries:
    print(f"\n--- Searching: {query} ---")
    try:
        results = tavily_search.invoke({"query": query})
        print("TYPE:", type(results))
        if isinstance(results, dict) and "results" in results:
            print("Num results:", len(results["results"]))
        else:
            print("UNEXPECTED SHAPE:", results)
    except Exception as e:
        print("EXCEPTION TYPE:", type(e))
        print("EXCEPTION:", repr(e))
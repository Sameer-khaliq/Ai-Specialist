import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch, TavilyExtract
from langgraph.graph import StateGraph, END
load_dotenv()
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)
print("all ok")


tavily_search = TavilySearch(
    max_results = 5,
    search_depth = "advanced",
    include_raw_content = False
)

tavily_extract = TavilyExtract(
    extract_depth = "advanced",
    format = "markdown"
)
# we are using langgraph and there our goal is to create a research agent which can perform research tasks
# There will be 4 nodes: 1. Generate queries from the user input,  2. Search web from queries,  3.read urls of the queries generated  4. Synthesize the report

class ResearchState( TypedDict):
    topic: str
    search_queries: List[str]     # generated search queries
    search_results: List[dict]    # raw results from Tavily search
    urls: List[str]               # extracted URLs to read
    url_contents: List[str]       # full content from each URL
    report: str                   # final synthesized report
    error: str                    # error generated


# _______Node 1: Query_Generator________
# It will take the topic as an input and generate 3 Queries

def generate_queries(state: ResearchState)-> dict:
    topic = state['topic']

    print(f'Node1 (Generate queries) running: Generating queries for the {topic}')

    prompt = f"""You are a research assistant. Generate exactly 3 specific, 
            different search queries to comprehensively research this topic: "{topic}"
            Return ONLY the 3 queries, one per line. No numbering, no bullets, no explanation."""
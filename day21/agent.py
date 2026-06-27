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
    response = llm.invoke(prompt)
    queries = [q.strip() for q in response.content.strip().split('\n') if q.strip()]
    queries = queries[:3]
    print(f"Node 1 executed: {queries}")
    return{"search_queries": queries}


#________Node 2: Web_search_________
# Runs each query through tavily, collects results and URLs

def search_web(state: ResearchState)-> dict:
    
    queries = state["search_queries"]
    all_results = []
    all_urls = []
    seen_urls = set()

    for query in queries:
        print(f"Node(2) is searching {query}.....")
        try:
            results = tavily_search.invoke({'query': query})
            # results is a list of dicts with keys: url, content, title, score
            if isinstance(results, list) and 'results' in results:
                for r in results:
                    url =r.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_urls.append(url)
                        all_results.append(url)
            elif isinstance(results, dict) and 'results' in results:
                for r in results['results']:
                    url = r.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_urls.append(url)
                        all_results.append(url)
        except Exception as e:
            print(f"Node 2 got error while running, error is: {e}")
        top_urls= all_urls[:5]
        top_results = all_results[:5]
        print(f"Node [2] found {len(top_urls)} in searching.")
        return{ 'search_results': top_results, 'urls': top_urls}

#_________Node 3: Reading URLs_________

def read_urls(state: ResearchState)-> dict:
    urls = state['urls']
    search_results = state['search_results']

    if not urls:
        return{'url_contents': [], "error": "No url found!!!"}
    contents =[]
    print(f"Node (3) Reading {len(urls)} urls ......")

    try:
        result = tavily_extract.invoke({'urls': urls})
        extracted = result.get('results', [])

        for item in extracted:
            url = item.get("url","")
            raw = item.get("raw_content", "")
            if raw:
                truncated = raw[:2000]
                contents.append(f"SOURCE: {url}\n\n{truncated}\n\n---")
    except Exception as e:
        print(f"Node (3) Extract error: {e}")
        
        print("Node (3) Falling back to search snippets...")
        for r in search_results:
            snippet = r.get("content", "")
            url = r.get("url", "")
            if snippet:
                contents.append(f"SOURCE: {url}\n\n{snippet}\n\n---")

    print(f"[Node 3] Read {len(contents)} sources successfully")
    return {"url_contents": contents}
    

#_________Node 4: Synthesize Report_________

# The heart of the agent — LLM reads all content and writes the report

def synthesize_report(state: ResearchState)->dict:
    topic = state["topic"]
    contents = state["url_contents"]
    search_results = state["search_results"]

    if not contents:
        return {"report": "No content could be retrieved for synthesis.", "error": "empty_content"}
    sources_list = "\n".join([
        f"- {r.get('title', 'Unknown')} ({r.get('url', '')})"
        for r in search_results[:5]
    ])

    all_content = "\n\n".join(contents)

    print(f"[Node 4] Synthesizing report from {len(contents)} sources...")

    prompt = f"""You are an expert research analyst. Based on the web sources below, 
            write a comprehensive, well-structured research report on: "{topic}"

            WEB SOURCES:
            {all_content}

            Write the report in this EXACT structure:

            # {topic}: Research Report

            ## Executive Summary
            (2-3 sentence overview of key findings)

            ## Key Findings
            (5-7 bullet points of the most important facts and insights)

            ## Detailed Analysis
            (3-4 paragraphs of in-depth analysis, organized by subtopic)

            ## Current Trends & Developments
            (What is happening right now in this space)

            ## Conclusion
            (1-2 paragraph wrap-up with key takeaways)

            ## Sources
            {sources_list}

            Rules:
            - Be factual and cite information from the sources
            - Be comprehensive but concise
            - Use markdown formatting throughout
            - Do not hallucinate — only use info from the provided sources"""
    response = llm.invoke(prompt)
    report = response.content

    print(f"[Node 4] Report generated ({len(report)} chars)")
    return {"report": report}
def build_research_agent():
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("generate_queries", generate_queries)
    graph.add_node("search_web", search_web)
    graph.add_node("read_urls", read_urls)
    graph.add_node("synthesize_report", synthesize_report)

    # Add edges — linear pipeline
    graph.set_entry_point("generate_queries")
    graph.add_edge("generate_queries", "search_web")
    graph.add_edge("search_web", "read_urls")
    graph.add_edge("read_urls", "synthesize_report")
    graph.add_edge("synthesize_report", END)

    return graph.compile()
def run_research(topic: str) -> str:
    if not topic or not topic.strip():
        return "Please enter a research topic."

    agent = build_research_agent()

    initial_state = ResearchState(
        topic=topic.strip(),
        search_queries=[],
        search_results=[],
        urls=[],
        url_contents=[],
        report="",
        error="",
    )

    try:
        result = agent.invoke(initial_state)
        return result.get("report", "No report generated.")
    except Exception as e:
        return f"Agent error: {str(e)}\n\nPlease try again or check your API keys."


if __name__ == "__main__":
    report = run_research("Scope of freelancing in ai agents niche 2026")
    print(report)
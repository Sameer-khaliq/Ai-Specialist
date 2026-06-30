import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch, TavilyExtract
from langgraph.graph import StateGraph, END
from langsmith import traceable

load_dotenv(r"C:\ai-specialist\.env")

# ── LangSmith tracing setup ────────────────────────────────────────────────
# These can also live in your .env file instead of here. Either works —
# just make sure they're set BEFORE any LangChain/LangGraph calls happen.
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_PROJECT", "day22-observability")
# LANGCHAIN_API_KEY should be in your .env file, not hardcoded here.

print("TAVILY KEY:", os.getenv("TAVILY_API_KEY", "NOT FOUND")[:5])
print("GROQ KEY:", os.getenv("GROQ_API_KEY", "NOT FOUND")[:5])
print("LANGSMITH KEY:", os.getenv("LANGCHAIN_API_KEY", "NOT FOUND")[:5])
print("LANGSMITH PROJECT:", os.getenv("LANGCHAIN_PROJECT"))

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)
print("LLM ok")

tavily_search = TavilySearch(
    max_results=5,
    search_depth="basic",
    include_raw_content=False,
)

tavily_extract = TavilyExtract(
    extract_depth="basic",
    format="markdown",
)


class ResearchState(TypedDict):
    topic: str
    search_queries: List[str]
    search_results: List[dict]
    urls: List[str]
    url_contents: List[str]
    report: str
    error: str


@traceable(name="generate_queries")
def generate_queries(state: ResearchState) -> dict:
    topic = state['topic']
    print(f'[Node 1] Generating queries for: {topic}')

    prompt = f"""You are a research assistant. Generate exactly 3 specific, 
            different search queries to comprehensively research this topic: "{topic}"
            Return ONLY the 3 queries, one per line. No numbering, no bullets, no explanation."""

    response = llm.invoke(prompt)
    queries = [
        q.strip().strip('"').strip("'")
        for q in response.content.strip().split("\n")
        if q.strip()
    ]
    queries = queries[:3]
    print(f"[Node 1] Queries: {queries}")
    return {"search_queries": queries}


@traceable(name="search_web")
def search_web(state: ResearchState) -> dict:
    queries = state["search_queries"]
    all_results = []
    all_urls = []
    seen_urls = set()

    for query in queries:
        print(f"[Node 2] Searching: {query}")
        try:
            results = tavily_search.invoke({"query": query})
            print(f"[Node 2][DEBUG] type={type(results)}")
            if isinstance(results, dict):
                print(f"[Node 2][DEBUG] keys={list(results.keys())}")
                if "error" in results:
                    print(f"[Node 2][DEBUG] ERROR CONTENT: {results['error']}")

            if isinstance(results, list):
                for r in results:
                    url = r.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_urls.append(url)
                        all_results.append(r)

            elif isinstance(results, dict) and "results" in results:
                for r in results["results"]:
                    url = r.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_urls.append(url)
                        all_results.append(r)

        except Exception as e:
            import traceback
            print(f"[Node 2] Search error for '{query}': {e}")
            traceback.print_exc()

    top_urls = all_urls[:5]
    top_results = all_results[:5]
    print(f"[Node 2] Found {len(top_urls)} unique URLs")
    if not top_urls:
        print(f"[Node 2][DEBUG] all_results was empty. Check Tavily API key/quota.")
    return {"search_results": top_results, "urls": top_urls}


@traceable(name="read_urls")
def read_urls(state: ResearchState) -> dict:
    urls = state["urls"]
    search_results = state["search_results"]

    if not urls:
        return {"url_contents": [], "error": "No URLs found"}

    contents = []
    print(f"[Node 3] Reading {len(urls)} URLs...")

    try:
        result = tavily_extract.invoke({"urls": urls})
        extracted = result.get("results", [])

        for item in extracted:
            url = item.get("url", "")
            raw = item.get("raw_content", "")
            if raw:
                truncated = raw[:2000]
                contents.append(f"SOURCE: {url}\n\n{truncated}\n\n---")

    except Exception as e:
        print(f"[Node 3] Extract error: {e}")
        print("[Node 3] Falling back to search snippets...")
        for r in search_results:
            snippet = r.get("content", "")
            url = r.get("url", "")
            if snippet:
                contents.append(f"SOURCE: {url}\n\n{snippet}\n\n---")

    print(f"[Node 3] Read {len(contents)} sources successfully")
    return {"url_contents": contents}


@traceable(name="synthesize_report")
def synthesize_report(state: ResearchState) -> dict:
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
    print(f"[Node 4] Synthesizing from {len(contents)} sources...")

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
            - Be factual, use only info from sources
            - Use markdown formatting
            - Do not hallucinate"""

    response = llm.invoke(prompt)
    report = response.content
    print(f"[Node 4] Report generated ({len(report)} chars)")

    import re
    from datetime import datetime

    safe_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic)
    safe_topic = safe_topic.strip().replace(' ', '_')[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{safe_topic}_{timestamp}.md"

    output_dir = r"C:\ai-specialist\day22"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[Node 4] Report saved: {filepath}")

    return {"report": report}


def build_research_agent():
    graph = StateGraph(ResearchState)
    graph.add_node("generate_queries", generate_queries)
    graph.add_node("search_web", search_web)
    graph.add_node("read_urls", read_urls)
    graph.add_node("synthesize_report", synthesize_report)
    graph.set_entry_point("generate_queries")
    graph.add_edge("generate_queries", "search_web")
    graph.add_edge("search_web", "read_urls")
    graph.add_edge("read_urls", "synthesize_report")
    graph.add_edge("synthesize_report", END)
    return graph.compile()


# ── Singleton pattern (Day 21 fix) ─────────────────────────────────────────
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        print("[Agent] Building graph (first call only)...")
        _agent = build_research_agent()
    return _agent


def run_research(topic: str, session_id: str = "default_session") -> str:
    if not topic or not topic.strip():
        return "Please enter a research topic."

    agent = get_agent()
    initial_state = ResearchState(
        topic=topic.strip(),
        search_queries=[],
        search_results=[],
        urls=[],
        url_contents=[],
        report="",
        error="",
    )

    # Metadata + tags — this is what lets you filter/analyze runs in
    # the LangSmith dashboard later (by user, session, query type, etc.)
    config = {
        "metadata": {
            "session_id": session_id,
            "query_type": "research",
            "topic": topic.strip()[:100],
        },
        "tags": ["production", "research-agent", "day22"],
    }

    try:
        result = agent.invoke(initial_state, config=config)
        return result.get("report", "No report generated.")
    except Exception as e:
        return f"Agent error: {str(e)}"


if __name__ == "__main__":
    report = run_research("Scope of freelancing in AI agents 2026")
    print(report)
import math
import chromadb
from dotenv import load_dotenv
from langchain_core.tools import Tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

CHROMA_DIR = "day12/chroma_db"
COLLECTION_NAME = "day12_collection"



# we will be making three funtions: calculator , knowledgeBaseRetriever and websearch here, so llm chooses what to do

# first we are making a safe calculator that excludes the __builtins__ to make our system safe

def safe_calculator( expression: str)-> str:
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error occurred: {e}"


def raw_retrieve(query: str, k : int = 3)->str:
    embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    client = chromadb.PersistentClient(path =CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    query_embed = embedding_model.embed_query(query)

    results = collection.query(query_embeddings = [query_embed], n_results = k)
    if not results or not results.get("documents") or not results["documents"][0]:
        return "No relevant information found in the knowledge base."

    return "\n\n".join(results["documents"][0])


def build_tools()->list[Tool]:
    calculator_tool = Tool(
        name = "Calculator",
        func = safe_calculator,
        description=(
            "Use for any math calculation. Input must be a valid Python math "
            "expression, e.g. '847 * 23' or 'sqrt(1764)'."
        )
    )

    retriever_tool = Tool(
        name="KnowledgeBaseRetriever",
        func=raw_retrieve,
        description=(
            "Use for questions about types of computers or types of databases — "
            "this is the only source of that information. Input should be the question."
        ),
    )

    web_search_tool = TavilySearchResults(
        max_results=3,
        name="WebSearch",
        description=(
            "Use for current events, today's date, real-time facts, or anything "
            "NOT about computers/databases."
        ),
    )

    return [calculator_tool, retriever_tool, web_search_tool]
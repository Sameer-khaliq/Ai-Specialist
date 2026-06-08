import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.tools import QueryEngineTool
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
import time
load_dotenv()

# settings of models

Settings.llm = GoogleGenAI(
    model = "gemini-2.5-flash",
    api_key = os.environ.get("GEMINI_API_KEY")
)

Settings.embed_model = GoogleGenAIEmbedding(
    model_name = "gemini-embedding-2",
    api_key = os.environ.get("GEMINI_API_KEY")
)

# LOADING DOCUMENTS IN SEPARATE INDEXES
print("Loading docs........")
policy_docs = SimpleDirectoryReader(input_files = ["day04/documents/company_policy.txt"]).load_data()
product_docs = SimpleDirectoryReader(input_files = ["day04/documents/product_manual.docx"]).load_data()
financial_docs = SimpleDirectoryReader(input_files = ["day04/documents/financial_report.pdf"]).load_data()

policy_index = VectorStoreIndex.from_documents(policy_docs)
product_index = VectorStoreIndex.from_documents(product_docs)
financial_index = VectorStoreIndex.from_documents(financial_docs)

tools =[
    QueryEngineTool.from_defaults(
        query_engine = policy_index.as_query_engine(),
        description = "Use this tool for questions about company HR policies, leaves, remote work, and employee guidelines."
    ),
    QueryEngineTool.from_defaults(
        query_engine = product_index.as_query_engine(),
        description = "Use this tool for questions about AI Assistant Pro product manual, software requirements, installation steps, and troubleshooting."
    ),
    QueryEngineTool.from_defaults(
        query_engine = financial_index.as_query_engine(),
        description = "Use this tool for questions about corporate financial data, Q3 revenue, net profits, expenses, and growth forecasts."
    )
]

#create router query engine

router_engine = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(), # LLM single choice select karega
    query_engine_tools=tools,
    verbose=True
)

queries = [
    "What is the maternity leave policy?",       
    "What was net profit in Q3?",                
    "How do I fix API errors in the product?"    
]

for q in queries:
    print(f"\n{'='*60}")
    print(f"User Query: {q}")
    response = router_engine.query(q)
    print(f"Final Answer: {response}")
    time.sleep(15)
    print("Waiting 15 seconds for api cooldown...")
#RouterQueryEngine user ke sawal ke mutabiq sahi description wale tool/index ko select karta hai aur query sirf usi specific file par bhejta hai.
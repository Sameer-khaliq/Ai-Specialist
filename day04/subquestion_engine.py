import os
import time
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
# SubQuestion components
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool
# Google GenAI packages
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core.question_gen import LLMQuestionGenerator

load_dotenv()

# Setup Models
Settings.llm = GoogleGenAI(
    model="gemini-2.5-flash",
    api_key=os.environ.get("GEMINI_API_KEY")
)
Settings.embed_model = GoogleGenAIEmbedding(
    model_name="gemini-embedding-2",
    api_key=os.environ.get("GEMINI_API_KEY")
)

print("Loading files individually...")
policy_docs = SimpleDirectoryReader(input_files=["day04/documents/company_policy.txt"]).load_data()
finance_docs = SimpleDirectoryReader(input_files=["day04/documents/financial_report.pdf"]).load_data()
product_docs = SimpleDirectoryReader(input_files=["day04/documents/product_manual.docx"]).load_data()

print("Building dedicated indexes...")
policy_index = VectorStoreIndex.from_documents(policy_docs)
finance_index = VectorStoreIndex.from_documents(finance_docs)
product_index = VectorStoreIndex.from_documents(product_docs)

# Tools setup (SubQuestionEngine requires unique 'name' attribute)
tools = [
    QueryEngineTool.from_defaults(
        query_engine=policy_index.as_query_engine(),
        name="company_policy_tool",
        description="Use this for questions about company HR policies, leaves, remote work, and employee guidelines."
    ),
    QueryEngineTool.from_defaults(
        query_engine=finance_index.as_query_engine(),
        name="financial_report_tool",
        description="Use this for questions about corporate financial data, Q3 revenue, net profits, expenses, and growth forecasts."
    ),
    QueryEngineTool.from_defaults(
        query_engine=product_index.as_query_engine(),
        name="product_manual_tool",
        description="Use this for questions about AI Assistant Pro product manual, software requirements, installation steps, and troubleshooting."
    )
]

# ─────────────────────────────────────────────
# STEP 4: Create the SubQuestion Query Engine
# ─────────────────────────────────────────────
question_gen_instance = LLMQuestionGenerator.from_defaults(llm=Settings.llm)

sub_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=tools,
    question_gen=question_gen_instance,  
    verbose=True
)
# Complex Query 
print("\n" + "="*60)
complex_query = """
Give me a quick company summary: 
What is the main product and its RAM requirement? 
How much was the Q3 net profit? 
And how many annual leaves do we get?
"""

print(f"Complex Query: {complex_query}")
print("Gemini is breaking down the question... (Ruk jaa 2 min)")

# Execution
response = sub_engine.query(complex_query)

print(f"\nFINAL COMBINED ANSWER:\n{response}")
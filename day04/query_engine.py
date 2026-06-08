from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from dotenv import load_dotenv
import os

load_dotenv()

# Settings of required models 
Settings.llm = GoogleGenAI(
    model = "gemini-2.5-flash",
    api_key = os.environ.get("GEMINI_API_KEY")
)

Settings.embed_model = GoogleGenAIEmbedding(
    model_name = "gemini-embedding-2",
    api_key = os.environ.get("GEMINI_API_KEY")
)

#----------------------
#step1: Load documents
#----------------------

documents = SimpleDirectoryReader("day04/documents").load_data()
print(f"{len(documents)} documents loaded")

index = VectorStoreIndex.from_documents(documents) # will do chunking,embedding, vector storage and indexing
query_engine = index.as_query_engine()
questions = [
    "How many annual leaves do employees get?",
    "What was the revenue in Q3 2024?",
    "What are the system requirements for AI Assistant Pro?"
]

for q in questions:
    print(f"Question: {q}")
    response = query_engine.query(q)
    print(f"Answer: {response}")
    print(f"Source nodes: {len(response.source_nodes)}")


    # Process
    #Documents → Chunks → Embeddings → Vector Store -> Query → Embed query → Find similar chunks → LLM → Answer
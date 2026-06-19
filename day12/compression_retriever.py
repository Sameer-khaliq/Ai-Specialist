import chromadb
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIR = "day12/chroma_db"

def build_metadata_filter(category: str = None, source:str = None) -> dict:
    conditions = []
    if category:
        conditions.append({"category": category})
    if source:
        conditions.append({"source": source})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def retrieve_and_compress( query:str, category:str = None, source:str = None, k: int = 5)->list[Document]:
   
    # embeddings of query
    embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    client = chromadb.PersistentClient(path = PERSIST_DIR)
    collection = client.get_collection("day12_collection")
    query_embed = embedding_model.embed_query(query)
   

    where_filter = build_metadata_filter(category= category, source = source)


    search_args = {
        "query_embeddings" : [query_embed],
        "n_results" : k
    }

    if where_filter:
        search_args["where"] = where_filter
    
    results = collection.query(**search_args)

    if not results or not results.get("documents") or not results["documents"][0]:
        return []
    
    retrieved_docs = []

    for doc_text, metadata in zip(results["documents"][0], results["metadatas"][0]):
        retrieved_docs.append(Document(page_content=doc_text, metadata=metadata)) # used defined Document format
    

    print(f"\n--- Compressing {len(retrieved_docs)} raw chunks down to core relevant lines... ---")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    compressed_docs = []

    for doc in retrieved_docs:  
        prompt = (
            f"Given the following target question, extract ONLY the exact sentences, facts, or parts "
            f"from the document context that are directly relevant to answering it.\n"
            f"Do not extrapolate, do not add filler text, and do not synthesize an answer.\n"
            f"If the document contains no relevant information, respond with exactly empty string ''.\n\n"
            f"Question: {query}\n"
            f"Document Context:\n{doc.page_content}\n\n"
            f"Extracted Relevant Facts:"
        )
        
        response = llm.invoke(prompt)
        extracted_content = response.content.strip()
        if extracted_content and extracted_content != "''":
            compressed_docs.append(
                Document(page_content=extracted_content, metadata=doc.metadata)
            )
            
    return compressed_docs
    



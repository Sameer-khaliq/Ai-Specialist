import os
from dotenv import load_dotenv
from pypdf import PdfReader
import time

load_dotenv()

def extract_pdf (filepath : str) -> str:
    filepath = r"C:\ai-specialist\test.pdf"
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return ""

    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text


def chunk_text( text:str , chunk_size: int = 500, overlap: int = 50)-> list[str]:
    #function will return the chunks of 500 characters, overlap will make sure to have the complete sentences and context of next abnd previous 
    chunks = []
    start = 0
    text_len = len(text)

    while start< text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap) 
    return chunks


from google import genai
from google.genai import types


client = genai.Client()

def get_embedding(text: str, is_query: bool = False) -> list[float]:
    task_type = "RETRIEVAL_QUERY" if is_query else "RETRIEVAL_DOCUMENT"
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type)
    )
    
    # API directly returns list of floats inside the embedded content structure
    return response.embeddings[0].values

import chromadb

# EphemeralClient memory-isolated local testing ke liye best hai
chroma_client = chromadb.EphemeralClient()
collection = chroma_client.get_or_create_collection(name="pdf_knowledge_base")

def store_chunks(chunks: list[str]):
    
    for i, chunk in enumerate(chunks):
        vector = get_embedding(chunk, is_query=False)
        collection.add(
            embeddings=[vector],
            documents=[chunk],
            ids=[f"chunk_{i}"]
        )

def retrieve(query: str, top_k: int = 3) -> list[str]:
 
    query_vector = get_embedding(query, is_query=True)
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )
    # Chroma returns lists within lists for batches, parse structural output down
    return results['documents'][0] if results['documents'] else []
def generate_answer(query: str, context_chunks: list[str]) -> str:
    """
    Sufficient grounding layers generate karke target framework se evaluation layer execute karta hai.
    """
    context = "\n\n".join(context_chunks)
    
    prompt = f"""Answer the question based only on the following context. 
    If the information is not in the context, say "I do not have this information."

    Context:
    {context}

    Question: {query}

    Answer:"""
    
    # Generation pipeline through standard production flash engine
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def rag_pipeline(pdf_path: str, query: str) -> str:
    
    #Complete Naive RAG Orchestration layer.
    
    print("Extracting raw textual content from PDF...")
    text = extract_pdf (pdf_path)
    
    print(f"Total length of extracted text: {len(text)} characters.")
    chunks = chunk_text(text)
    print(f"Generated {len(chunks)} contextual chunks.")
    print("Waiting 30 seconds for api refreshment.....")
    time.sleep(30)
    
    print("Vectorizing chunks and seeding ChromaDB...")
    store_chunks(chunks)
    print("Waiting for another 30 seconds for response.........")
    time.sleep(30)
    
    print(f"Computing vector distance for query: '{query}'...")
    relevant_chunks = retrieve(query, top_k=3)
    print("Waiting for another 70 seconds for response.........")
    time.sleep(70)
    print("Formulating structured grounded answer response...")
    answer = generate_answer(query, relevant_chunks)
    return answer
if __name__ == "__main__":
    # Make sure sample.pdf exists in the directory path
    pdf_file_path = "test.pdf"
    test_query = "What are the core arguments or topics detailed in this document?"
    
    if os.path.exists(pdf_file_path):
        final_response = rag_pipeline(pdf_file_path, test_query)
        print("\n=== SYSTEM RESPONSE ===")
        print(final_response)
    else:
        print(f"[!] Target path error: {pdf_file_path} not found. Drop a dummy PDF file to verify pipeline.")
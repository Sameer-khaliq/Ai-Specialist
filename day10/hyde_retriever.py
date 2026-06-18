import sys
import time
from pypdf import PdfReader
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm =ChatGoogleGenerativeAI(model = "gemini-2.5-flash")
embeddings_model = GoogleGenerativeAIEmbeddings(model = "models/gemini-embedding-001")

def extract_pdf(filepath:str, chunk_size:int = 500) -> list[str]:
    reader = PdfReader(filepath)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    words = full_text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1

        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def build_dense_index(chunks: list[str]):
    client = chromadb.Client()

    try:
        client.delete_collection("hyde_search")
    except:
        pass
    collection = client.create_collection("hyde_search")
    embeds = embeddings_model.embed_documents(chunks)

    collection.add(
        documents = chunks,
        embeddings = embeds,
        ids = [str(i) for i in range(len(chunks))] 
    )
    return collection

def generate_hypothetical_answer(query: str) -> str:

    prompt = f"""Answer the following question in 3-4 sentences as if you are
    writing a factual passage from a textbook. Be specific and detailed,
    even if you are not 100% sure of the answer.

    Question: {query}

    Answer:"""
    hyp_response = llm.invoke(prompt)
    return hyp_response.content


def hyde_search(collection, hypothetical_answer: str, top_k: int = 5)-> list[str]:

    hyp_ans_embeddings = embeddings_model.embed_query(hypothetical_answer)

    results = collection.query(
        query_embeddings = [hyp_ans_embeddings],
        n_results = top_k
    )
    return results["documents"][0]

def naive_search( query: str, collection, top_k: int = 5) -> list[str]:
    query_embedding = embeddings_model.embed_query(query)

    results = collection.query(
        query_embeddings = [query_embedding],
        n_results = top_k
    )

    return results["documents"][0]

#__________Main function_______________

test_queries = [
    
    "what is client server database architecture",
 
    # Single-tier
    "what is single tier database architecture",
   
    # Homogeneous / Heterogeneous
    "what is a homogeneous distributed database",

 
    # Vague / conceptual (HyDE often helps more here)
    "which database architecture is most secure for online banking",
    "how does data stay reliable when spread across multiple locations",
]
def cooldown(seconds: int = 60):
    print("Waiting for API cooldown...")
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rCooldown active: {remaining} seconds remaining... ")
        sys.stdout.flush()
        time.sleep(1)
    print("\rCooldown complete! Resuming code execution.        \n")
 
# ─── MAIN ────────────────────────────────────────────────────────────────────
 
if __name__ == "__main__":
    pdf_path = "day10/test.pdf"
    print("PDF load ho rahi hai...")
    chunks = extract_pdf(pdf_path)
    print(f"Total chunks created: {len(chunks)}")
 
    print("\nChromaDB index ban raha hai...")
    collection = build_dense_index(chunks)
    print("Database ready!")
 
    results_log = []
 
    for i, query in enumerate(test_queries, start=1):
        print(f"\n{'='*60}\nQuery {i}/{len(test_queries)}: '{query}'\n{'='*60}")
 
        cooldown(60)
        hyp_answer = generate_hypothetical_answer(query)
        print(f"Hypothetical Answer:\n{hyp_answer}\n")
 
        cooldown(60)
        naive_result = naive_search(query, collection, top_k=1)[0]
        print(f"--- Naive RAG Result ---\n{naive_result[:200]}...\n")
 
        cooldown(60)
        hyde_result = hyde_search(collection, hyp_answer, top_k=1)[0]
        print(f"--- HyDE Result ---\n{hyde_result[:200]}...\n")
 
        results_log.append({
            "query": query,
            "hypothetical_answer": hyp_answer,
            "naive_result": naive_result,
            "hyde_result": hyde_result,
        })
 
    # Sab results ek file mein save karo taake comparison table banana easy ho
    with open("day10/results_log.txt", "w", encoding="utf-8") as f:
        for r in results_log:
            f.write(f"QUERY: {r['query']}\n")
            f.write(f"NAIVE: {r['naive_result'][:200]}\n")
            f.write(f"HYDE: {r['hyde_result'][:200]}\n")
            f.write("-" * 60 + "\n")
 
    print("\nAll 20 queries done. Results saved to day10/results_log.txt")

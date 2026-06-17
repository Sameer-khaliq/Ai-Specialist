import os
import time
from pypdf import PdfReader
from rank_bm25 import BM25Okapi
import chromadb
from google import genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


#step1: Extracting text from pdf

def extract_pdf(filepath: str, chunk_size:int = 500 ) -> list[str]:
    reader = PdfReader(filepath)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    # chunking
    words = full_text.split()
    chunks = []
    current_chunk = []
    current_len = 0

    for word in words:
        current_chunk.append(word)
        current_len += len(word) + 1
        if current_len >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0
        
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


# Step 2:  Build bm25 index

def build_bm25_index(chunks: list[str]) -> BM25Okapi:
    #tokenizing the chunks
    tokenized = [chunk.lower().split() for chunk in chunks]
    return BM25Okapi(tokenized)


# Step 3: Build chromadb index

def build_dense_index(chunks: list[str]):
    embeddings_model = GoogleGenerativeAIEmbeddings(model= "models/gemini-embedding-001")
    client = chromadb.Client()

    collection = client.create_collection("hybrid_search")

    embeds = embeddings_model.embed_documents(chunks)
    
    collection.add(
        embeddings= embeds,
        documents = chunks,
        ids= [str(i) for i in range (len(chunks))]
    )

    return collection, embeddings_model


def reciprocal_rank_fusion(bm25_results: list[str], dense_results: list[str], k:int = 60)-> list[str]:
    scores = {}
    for rank, (doc, _) in enumerate(bm25_results):
        scores[doc] = (scores.get(doc, 0) + 1 /(k+ rank + 1))
    for rank, (doc) in enumerate(dense_results):
        scores[doc] = (scores.get(doc, 0) + 1 /(k+ rank + 1))
    
    ranked_results = sorted(scores.items(), key = lambda x : x[1], reverse = True)
    return ranked_results
    
def hybrid_search(
        query: str,
        chunks: list[str],
        bm25_index,
        dense_index,
        embeddings_model,
        top_k: int = 3
):
    # bm25 matching
    tokenized_query = query.lower().split()
    bm25_scores =bm25_index.get_scores(tokenized_query)
    bm25_indices = sorted(enumerate(bm25_scores), key = lambda x: x[1], reverse = True)[:top_k]
    bm25_results = [(chunks[i], score) for i, score in bm25_indices]

    # dense results matching

    query_vector = embeddings_model.embed_query(query)
    dense_response = dense_index.query(query_embeddings = [query_vector], n_results = top_k)
    dense_results = dense_response["documents"][0]

    fused_results = reciprocal_rank_fusion(bm25_results, dense_results)

    return [doc for doc, score in fused_results[:top_k]]
# ─── Execution ─────────────────────────────────────────────────────────────

chunks = extract_pdf("day09/test.pdf")
print(f"Total Chunks: {len(chunks)}")

print("Building BM25 Index...")
bm25_index = build_bm25_index(chunks)

print("Waiting for api cool down (60 seconds)...")
time.sleep(60)

print("Building Dense Index...")
dense_index, embeddings_model = build_dense_index(chunks)
print("Indexes Ready!\n" + "="*40)

# Ab aap aram se test kar sakte hain:
test_query = "what is a centralized database"
print(f"Query: {test_query}")

search_results = hybrid_search(test_query, chunks, bm25_index, dense_index, embeddings_model, top_k=2)

for i, res in enumerate(search_results):
    print(f"\n--- Top Result {i+1} ---")
    print(res[:300] + "...")
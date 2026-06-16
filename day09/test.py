import os
from pypdf import PdfReader
from rank_bm25 import BM25Okapi
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# ─── STEP 1: PDF se text extract karo ───────────────────────────────────────

def load_pdf_chunks(pdf_path: str, chunk_size: int = 500) -> list[str]:
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    # Simple chunking — har 500 characters ka ek chunk
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


# ─── STEP 2: BM25 index banao ───────────────────────────────────────────────

def build_bm25_index(chunks: list[str]) -> BM25Okapi:
    tokenized = [chunk.lower().split() for chunk in chunks]
    return BM25Okapi(tokenized)


# ─── STEP 3: ChromaDB index banao ───────────────────────────────────────────

def build_dense_index(chunks: list[str]):
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    client = chromadb.Client()

    # Agar collection pehle se hai toh delete
    try:
        client.delete_collection("hybrid_search")
    except:
        pass

    collection = client.create_collection("hybrid_search")

    print("Embedding chunks... (thoda waqt lagega)")
    embeds = embeddings_model.embed_documents(chunks)

    collection.add(
        documents=chunks,
        embeddings=embeds,
        ids=[str(i) for i in range(len(chunks))]
    )

    return collection, embeddings_model


# ─── STEP 4: RRF fusion ─────────────────────────────────────────────────────

def reciprocal_rank_fusion(bm25_results: list, dense_results: list, k: int = 60) -> list:
    """
    Dono lists ke ranks combine karo.
    Higher score = better result.
    """
    scores = {}

    # BM25 results mein rank assign 
    for rank, (doc, _) in enumerate(bm25_results):
        scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)

    # Dense results mein rank assign
    for rank, doc in enumerate(dense_results):
        scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)

    # Score ke hisaab se sort 
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked


# ─── STEP 5: Hybrid search function ─────────────────────────────────────────

def hybrid_search(
    query: str,
    chunks: list[str],
    bm25_index: BM25Okapi,
    collection,
    embeddings_model,
    top_k: int = 5
) -> list[str]:

    # BM25 search
    tokenized_query = query.lower().split()
    bm25_scores = bm25_index.get_scores(tokenized_query)
    bm25_top = sorted(enumerate(bm25_scores), key=lambda x: x[1], reverse=True)[:top_k]
    bm25_results = [(chunks[i], score) for i, score in bm25_top]

    # Dense search
    query_embedding = embeddings_model.embed_query(query)
    dense_response = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    dense_results = dense_response["documents"][0]

    # RRF fusion
    fused = reciprocal_rank_fusion(bm25_results, dense_results)

    # Top k return karo
    return [doc for doc, score in fused[:top_k]]


# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    PDF_PATH = "day09/test.pdf"

    print("PDF load ho rahi hai...")
    chunks = load_pdf_chunks(PDF_PATH)
    print(f"Total chunks: {len(chunks)}")

    print("BM25 index ban raha hai...")
    bm25_index = build_bm25_index(chunks)

    print("ChromaDB dense index ban raha hai...")
    collection, embeddings_model = build_dense_index(chunks)

    # Test queries
    test_queries = [
        "what is a vector database",
        "difference between relational and NoSQL databases",
        "how does indexing work in databases",
        "what is ACID compliance",
        "graph database use cases",
    ]

    print("\n" + "="*60)
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = hybrid_search(query, chunks, bm25_index, collection, embeddings_model, top_k=3)
        print(f"Top result: {results[0][:200]}...")
        print("-"*60)
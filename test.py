import os
from rank_bm25 import BM25Okapi
import chromadb
from chromadb.utils import embedding_functions

# =====================================================================
# STEP 1: INITIALIZING AND ENVIRONMENT SETUP
# =====================================================================

corpus_chunks = [
    "A centralized database architecture stores all structural data on a single unified machine node.",
    "Error Code E4042 represents a critical TCP connection handshake timeout failure within the network layer.",
    "Under Section 7.3.2, security protocols mandate that all API transport channels must enforce TLS 1.3 encryption.",
    "Client-server software architecture splits processing workloads between service providers and resource requesters.",
    "Database management systems use transactions to guarantee atomic updates, consistency, isolation, and durability.",
    "System error logs indicate that failing to resolve hostname parameters triggers Error Code E4042 instantly.",
    "Network engineering guidelines in Section 7.3.2 specify rigorous firewall rules for data isolation controls.",
    "Distributed database architectures partition data metrics globally across multiple regional cluster arrays."
]

print("-> Initializing Chroma Client...")
chroma_client = chromadb.Client()

print("-> Loading Local Embedding Model (Downloading weights if first time)...")
embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name = "all-MiniLM-L6-v2"
)
print("-> Model loaded successfully!")
collection = chroma_client.create_collection(
    name = "hybrid_collection",
    embedding_function = embedding_model
)

# FIXED: Added underscore delimiter to match parsing logic below
dense_ids = [f"chunk_{i}" for i in range(len(corpus_chunks))]

collection.add(
    ids = dense_ids,
    documents = corpus_chunks     
)

# =====================================================================
# SEARCH & RRF CORE INTERFACES
# =====================================================================

def build_bm25_index(chunks: list[str]) -> BM25Okapi:
    tokenized_chunks = [chunk.lower().split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    return bm25

def bm25_search(bm25: BM25Okapi, query: str, top_k: int = 5) -> list[tuple[int, float]]:
    tokenized_query = query.lower().split()
    raw_scores = bm25.get_scores(tokenized_query)
    indexed_scores = list(enumerate(raw_scores))
    ranked_results = sorted(indexed_scores, key=lambda x: x[1], reverse=True)
    return ranked_results[:top_k]

def dense_search(collection, query: str, top_k: int = 5) -> list[tuple[int, float]]:
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["distances"]
    )
    ids = results['ids'][0]
    distances = results['distances'][0]
    dense_ranked = []
    for chunk_id, distance in zip(ids, distances):
        # Works perfectly now because chunk_id is "chunk_X"
        integer_idx = int(chunk_id.split("_")[1])
        normalized_score = 1.0 - distance
        dense_ranked.append((integer_idx, normalized_score))
        
    return dense_ranked
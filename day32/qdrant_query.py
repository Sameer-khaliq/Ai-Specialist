from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
client = QdrantClient(host="localhost", port=6333)

query = "machine learning applications"
query_emb = model.encode(query).tolist()

# Plain search
results = client.query_points(
    collection_name="documents", 
    query=query_emb, 
    limit=5
).points
print("--- Plain Search ---")
for r in results:
    print(r.score, r.payload["content"][:60])

# Filtered search (payload filtering — Qdrant's strength)
filtered_results = client.search(
    collection_name="documents",
    query_vector=query_emb,
    query_filter=Filter(
        must=[FieldCondition(key="category", match=MatchValue(value="cat_1"))]
    ),
    limit=5
)
print("\n--- Filtered Search (category=cat_1) ---")
for r in filtered_results:
    print(r.score, r.payload["content"][:60])
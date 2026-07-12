from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
client = QdrantClient(host="localhost", port=6333)

# Load same sample data from Day 32
with open("day32/sample_texts.json", "r") as f:
    texts = json.load(f)

print("Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True)

# Create collection with HNSW config
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    hnsw_config={"m": 16, "ef_construct": 100}
)

# Batch upload
points = [
    PointStruct(
        id=i,
        vector=emb.tolist(),
        payload={"content": text, "category": f"cat_{i % 10}"}
    )
    for i, (text, emb) in enumerate(zip(texts, embeddings))
]

client.upsert(collection_name="documents", points=points)
print(f"Inserted {len(points)} points into Qdrant.")
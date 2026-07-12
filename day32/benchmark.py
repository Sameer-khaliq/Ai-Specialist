import time
import psycopg2
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
query_emb = model.encode("machine learning applications").tolist()

def bench_pgvector():
    conn = psycopg2.connect(dbname="vectordb", user="postgres", password="sameer", host="localhost", port="5433")
    cur = conn.cursor()
    start = time.perf_counter()
    cur.execute("SELECT content FROM documents ORDER BY embedding <=> %s::vector LIMIT 5;", (query_emb,))
    cur.fetchall()
    latency = (time.perf_counter() - start) * 1000
    cur.close()
    conn.close()
    return latency

def bench_qdrant():
    client = QdrantClient(host="localhost", port=6333)
    start = time.perf_counter()
    client.search(collection_name="documents", query_vector=query_emb, limit=5)
    latency = (time.perf_counter() - start) * 1000
    return latency

if __name__ == "__main__":
    results = {}
    for name, fn in [("pgvector", bench_pgvector), ("qdrant", bench_qdrant)]:
        times = [fn() for _ in range(10)]  # 10 runs for avg
        avg = sum(times) / len(times)
        results[name] = avg
        print(f"{name}: avg={avg:.2f}ms, min={min(times):.2f}ms, max={max(times):.2f}ms")
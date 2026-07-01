import os
import time
import json
import uuid
import numpy as np
import redis
import warnings
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from groq import Groq
from dotenv import load_dotenv
from gptcache import cache
from gptcache.manager import VectorBase
from gptcache.manager.data_manager import SSDataManager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class PureRedisScalarStorage:
    def __init__(self, url):
        self.client = redis.Redis.from_url(url)

    def batch_insert(self, cache_datas):
        ids = []
        pipeline = self.client.pipeline()
        for data in cache_datas:
            pk = int(uuid.uuid4().int & 0x7FFFFFFF)
            question_str = data.question.content if hasattr(data.question, "content") else str(data.question)
            if isinstance(data.answers, list):
                answers_str = [a.answer if hasattr(a, "answer") else str(a) for a in data.answers]
            else:
                answers_str = str(data.answers)
            payload = {
                "question": question_str,
                "answer": answers_str,
                "session_id": data.session_id or ""
            }
            pipeline.set(f"gptcache:scalar:{pk}", json.dumps(payload))
            ids.append(pk)
        pipeline.execute()
        return ids

    def get_detail(self, pk):
        res = self.client.get(f"gptcache:scalar:{pk}")
        if res:
            data = json.loads(res.decode("utf-8"))
            return data["question"], data["answer"]
        return None, None

    def get_ids(self, deleted=False):
        return []

    def close(self):
        self.client.close()


load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
REDIS_CLOUD_URL = os.environ.get("REDIS_CLOUD_URL")

gemini_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GEMINI_API_KEY
)
groq_client = Groq(api_key=GROQ_API_KEY)

EMBEDDING_DIMENSION = 3072

print("Initializing semantic cache...")
Path("./day24/gptcache_local").mkdir(parents=True, exist_ok=True)

cache_base = PureRedisScalarStorage(url=REDIS_CLOUD_URL)
vector_base = VectorBase(
    name="faiss",
    dimension=EMBEDDING_DIMENSION,
    index_path="./day24/gptcache_local/faiss.index"
)
data_manager = SSDataManager(
    s=cache_base, v=vector_base,
    o=None, e=None,
    max_size=1000, clean_size=200
)
cache.init(
    embedding_func=lambda text, **kw: np.array(
        gemini_embeddings.embed_query(
            text.get("messages", [{}])[-1].get("content", "") if isinstance(text, dict) else text
        ), dtype=np.float32
    ),
    data_manager=data_manager,
    similarity_evaluation=SearchDistanceEvaluation(),
)
print("Cache ready.\n")

# Clear previous cached data for a clean benchmark
import faiss
keys = cache_base.client.keys("gptcache:scalar:*")
if keys:
    cache_base.client.delete(*keys)
cache.data_manager.v._index = faiss.IndexIDMap(faiss.IndexFlatL2(EMBEDDING_DIMENSION))
print(f"Cleared {len(keys)} cached entries for clean benchmark.\n")


def ask_with_cache(prompt: str):
    start = time.time()
    embedding = np.array(gemini_embeddings.embed_query(prompt), dtype=np.float32)
    results = cache.data_manager.search(embedding, top_k=1)

    if results:
        pk = results[0][1] if isinstance(results[0], (list, tuple)) else results[0]
        _, cached_answer = cache_base.get_detail(pk)
        if cached_answer:
            return cached_answer, (time.time() - start) * 1000, "HIT"

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    output = response.choices[0].message.content
    cache.data_manager.save(prompt, output, embedding)
    return output, (time.time() - start) * 1000, "MISS"


# ── Benchmark dataset ─────────────────────────────────────────────────────────
# 6 base queries + 2 paraphrases each = 18 total queries
# First pass: all 6 base queries → all MISS, populate cache
# Second pass: 12 paraphrases → should all HIT semantically

base_queries = [
    "What is the difference between supervised and unsupervised learning?",
    "How does a transformer model work?",
    "What is RAG in the context of AI systems?",
    "Explain the concept of vector embeddings.",
    "What are the main use cases for LangGraph?",
    "How does Redis work as an in-memory data store?",
]

paraphrase_queries = [
    # paraphrases for query 1
    "Can you explain supervised vs unsupervised machine learning?",
    "What distinguishes supervised learning from unsupervised learning?",
    # paraphrases for query 2
    "How do transformer neural networks function?",
    "What is the architecture behind transformer models?",
    # paraphrases for query 3
    "What does RAG mean in AI?",
    "Can you explain retrieval augmented generation?",
    # paraphrases for query 4
    "What are vector embeddings and how are they used?",
    "How do embeddings represent text as vectors?",
    # paraphrases for query 5
    "What problems does LangGraph solve?",
    "When would you use LangGraph in an AI project?",
    # paraphrases for query 6
    "Why is Redis considered an in-memory database?",
    "How does Redis store and retrieve data so fast?",
]

results_log = []

# ── Phase 1: Populate cache with base queries ─────────────────────────────────
print("=" * 60)
print("PHASE 1 — Populating cache (base queries, expect all MISS)")
print("=" * 60)

for i, q in enumerate(base_queries, 1):
    ans, latency, status = ask_with_cache(q)
    results_log.append({"query": q, "type": "BASE", "status": status, "latency_ms": latency})
    print(f"  [{i}/{len(base_queries)}] {status} | {latency:.1f}ms | {q[:55]}...")

# ── Phase 2: Hit cache with paraphrases ───────────────────────────────────────
print(f"\n{'=' * 60}")
print("PHASE 2 — Semantic cache hit test (paraphrases, expect HIT)")
print("=" * 60)

for i, q in enumerate(paraphrase_queries, 1):
    ans, latency, status = ask_with_cache(q)
    results_log.append({"query": q, "type": "PARAPHRASE", "status": status, "latency_ms": latency})
    print(f"  [{i}/{len(paraphrase_queries)}] {status} | {latency:.1f}ms | {q[:55]}...")

# ── Aggregate stats ───────────────────────────────────────────────────────────
misses = [r for r in results_log if r["status"] == "MISS"]
hits = [r for r in results_log if r["status"] == "HIT"]

avg_miss_latency = sum(r["latency_ms"] for r in misses) / len(misses) if misses else 0
avg_hit_latency = sum(r["latency_ms"] for r in hits) / len(hits) if hits else 0
latency_reduction = ((avg_miss_latency - avg_hit_latency) / avg_miss_latency * 100) if avg_miss_latency else 0
api_calls_avoided = len(hits)
total_queries = len(results_log)

# Groq llama-3.3-70b pricing: $0.59 per 1M input tokens, $0.79 per 1M output tokens
# Rough estimate: avg 50 input + 300 output tokens per query
estimated_cost_per_call = (50 * 0.59 + 300 * 0.79) / 1_000_000
cost_saved = api_calls_avoided * estimated_cost_per_call

print(f"\n{'=' * 60}")
print("BENCHMARK RESULTS")
print("=" * 60)
print(f"Total queries run:        {total_queries}")
print(f"Cache MISS (API calls):   {len(misses)}")
print(f"Cache HIT  (no API call): {len(hits)}")
print(f"Cache hit rate:           {len(hits)/total_queries*100:.1f}%")
print(f"\nAvg latency — MISS:       {avg_miss_latency:.1f} ms")
print(f"Avg latency — HIT:        {avg_hit_latency:.1f} ms")
print(f"Latency reduction:        {latency_reduction:.1f}%")
print(f"\nAPI calls avoided:        {api_calls_avoided}")
print(f"Estimated cost saved:     ${cost_saved:.6f}")
print(f"  (based on Groq llama-3.3-70b pricing: $0.59/$0.79 per 1M tokens)")
print("=" * 60)

print("\nPER-QUERY BREAKDOWN")
print("-" * 60)
print(f"{'TYPE':<12} {'STATUS':<6} {'LATENCY':>10}  QUERY")
print("-" * 60)
for r in results_log:
    print(f"{r['type']:<12} {r['status']:<6} {r['latency_ms']:>8.1f}ms  {r['query'][:45]}...")
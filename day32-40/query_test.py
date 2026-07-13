import psycopg2
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
query = "machine learning applications"
query_emb = model.encode(query).tolist()

conn = psycopg2.connect(
    dbname="vectordb", user="postgres", password="sameer",
    host="localhost", port="5433"
)
cur = conn.cursor()
#testing
for op, name in [("<=>", "Cosine"), ("<->", "L2"), ("<#>", "Dot Product")]:
    cur.execute(f"""
        SELECT content, embedding {op} %s::vector AS distance
        FROM documents
        ORDER BY embedding {op} %s::vector
        LIMIT 5;
    """, (query_emb, query_emb))
    print(f"\n--- {name} ---")
    for row in cur.fetchall():
        print(row)

cur.close()
conn.close()
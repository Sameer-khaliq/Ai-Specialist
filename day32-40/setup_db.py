import psycopg2
 

conn = psycopg2.connect(
    dbname="vectordb",
    user="postgres",
    password="sameer",
    host="localhost",
    port="5433"
)

cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(384)
);
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS documents_hnsw_idx
ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
""")

conn.commit()
cur.close()
conn.close()
print("Table + HNSW index ready.")
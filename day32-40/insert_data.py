import psycopg2
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2') #https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

with open("day32/sample_texts.json", "r") as f:
    texts = json.load(f)

print("Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True)

conn = psycopg2.connect(
    dbname="vectordb", user="postgres", password="sameer",
    host="localhost", port="5433"
)
cur = conn.cursor()

for text, emb in zip(texts, embeddings):
    cur.execute(
        "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
        (text, emb.tolist())
    )

conn.commit()
cur.close()
conn.close()
print(f"Inserted {len(texts)} records.")
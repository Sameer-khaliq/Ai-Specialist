import os
from datetime import datetime
from pathlib import Path
from pypdf import PdfReader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import chromadb
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIR = "day12/chroma_db"

DOC_CATEGORIES={
    "day12/data/Types_of_computers.pdf" : "computers",
    "day12/data/Types_of_database.pdf" : "databases"
}


def extract_pdf(filepath: str, chunk_size: int = 500)-> list[str]:
    reader = PdfReader(filepath)
    full_text = ""
    chunks = []
    current_chunk = []
    current_length = 0

    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    words = full_text.split()


    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1

        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))


    return chunks 


def build_vector_store():
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    client = chromadb.PersistentClient(path = PERSIST_DIR)

    try:
        client.delete_collection("day12_collection")
    except:
        pass

    collection = client.create_collection("day12_collection")

    all_documents = []
    all_metadata = []

    for filepath, category in DOC_CATEGORIES.items():
        if not os.path.exists(filepath):
            print(f"File doesnot exist at{filepath}!!!!!!!!!")
            return
    

        raw_chunks = extract_pdf(filepath, chunk_size = 500)
        print(f"Loaded {len(raw_chunks)} chunks from {filepath} [category = {category}]")

        filename = Path(filepath).name
        ingest_date = datetime.now().strftime("%Y-%m-%d")

        for chunk in raw_chunks:
            if chunk.strip():
                all_documents.append(chunk)
                all_metadata.append({
                    "source": filename,
                    "category": category,
                    "date": ingest_date
                })
    
    ids = [f"id_{i}" for i in range(len(all_documents))]

    embeddings = embeddings_model.embed_documents(all_documents)

    collection.add(
        documents=all_documents,
        embeddings=embeddings,
        metadatas=all_metadata,
        ids=ids
    )
    print("Indexing done successfully!!!")


if __name__ == "__main__":
    build_vector_store()
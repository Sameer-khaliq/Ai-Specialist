from langchain_google_genai import GoogleGenerativeAIEmbeddings
import chromadb
from langchain_core.documents import Document
from compression_retriever import retrieve_and_compress, build_metadata_filter

PERSIST_DIR = "day12/chroma_db"

TEST_QUERIES = [
    "what is centralized database?",
    "what are tablet pc's?",
]


def raw_retrieval(query: str, k: int = 5) -> list[Document]:
    """Same retrieval steps as retrieve_and_compress(), minus the compression loop — our 'before' baseline."""
    embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_collection("day12_collection")
    query_embed = embedding_model.embed_query(query)

    results = collection.query(query_embeddings=[query_embed], n_results=k)
    if not results or not results.get("documents") or not results["documents"][0]:
        return []

    docs = []
    for doc_text, metadata in zip(results["documents"][0], results["metadatas"][0]):
        docs.append(Document(page_content=doc_text, metadata=metadata))
    return docs


def run_compression_test():
    total_raw, total_comp = 0, 0
    example_shown = False

    for q in TEST_QUERIES:
        raw_docs = raw_retrieval(q)
        comp_docs = retrieve_and_compress(q, k=5)

        raw_chars = sum(len(d.page_content) for d in raw_docs)
        comp_chars = sum(len(d.page_content) for d in comp_docs)
        total_raw += raw_chars
        total_comp += comp_chars

        print(f"Query: {q}")
        print(f"  raw_chars={raw_chars} -> compressed_chars={comp_chars}")

        if not example_shown and raw_docs and comp_docs:
            print("\n  --- SAMPLE BEFORE/AFTER ---")
            print(f"  BEFORE (raw chunk): {raw_docs[0].page_content[:300]}")
            print(f"  AFTER (compressed): {comp_docs[0].page_content[:300]}")
            print("  ---------------------------\n")
            example_shown = True

    reduction = round(100 * (1 - total_comp / total_raw), 1) if total_raw else 0
    print(f"Average compression reduction across {len(TEST_QUERIES)} queries: {reduction}%")
    return reduction


def run_filter_test():
    # Field 1: category only
    docs1 = retrieve_and_compress("types of computers", category="computers", k=5)
    cats = {d.metadata.get("category") for d in docs1}
    assert cats <= {"computers"}, f"FAIL: leaked categories {cats}"
    print(f"[category=computers] PASS — returned only: {cats}")

    # Field 2: category + source combined
    docs2 = retrieve_and_compress(
        "types of databases", category="databases", source="Types_of_database.pdf", k=5
    )
    srcs = {d.metadata.get("source") for d in docs2}
    assert srcs <= {"Types_of_database.pdf"}, f"FAIL: leaked sources {srcs}"
    print(f"[category=databases, source=Types_of_database.pdf] PASS — returned only: {srcs}")


if __name__ == "__main__":
    print("=== Compression Test (2 queries) ===")
    run_compression_test()

    print("\n=== Metadata Filter Test (2 fields) ===")
    run_filter_test()
# Configuration dictionary for pure local execution
local_mem0_config = {
    "vector_store": {
        "provider": "chromadb",
        "config": {
            "path": "./day18/chroma_db",
            "collection_name": "long_term_memories"
        }
    },
    "llm": {
        "provider": "google",
        "config": {
            "model": "gemini-2.5-flash"
        }
    },
    "embedder": {
        "provider": "google",
        "config": {
            "model": "gemini-embedding-001"
        }
    }
}
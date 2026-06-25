# Configuration dictionary for pure local execution
local_mem0_config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "path": "./day18/chroma_db",
            "collection_name": "long_term_memories"
        }
    },
    "llm": {
        "provider": "gemini",
        "config": {
            "model": "gemini-2.5-flash"
        }
    },
    "embedder": {
        "provider": "gemini",
        "config": {
            "model": "gemini-embedding-001"
        }
    }
}
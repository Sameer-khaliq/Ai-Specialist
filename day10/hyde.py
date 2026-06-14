def generate_hypothetical_answer(query: str) -> str:
    prompt = f"""Write a short, plausible passage that could answer this question. 
Write it as if it's an excerpt from a document — declarative, factual tone. 
Do not say "I don't know" — generate a plausible-sounding answer even if uncertain.

Question: {query}

Passage:"""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )
    return response.text
 def hyde_retrieve(query: str, collection, top_k: int = 3) -> list[str]:
        hypothetical_doc = generate_hypothetical_answer(query)
            
        results = collection.query(
        query_texts=[hypothetical_doc],  # hypothetical answer embed hoga, not original query
        n_results=top_k
            )
    
    return results['documents'][0]
def naive_retrieve(query: str, collection, top_k: int = 3) -> list[str]:
    results = collection.query(
        query_texts=[query],  # direct query embedding
        n_results=top_k
    )
    return results['documents'][0]##
test_queries = {
    "short_factual": [
        "What is E4042?",
        "Define centralized database",
        # ... 3 more
    ],
    "conversational": [
        "Can you explain how client-server systems work?",
        "I'm confused about database transactions, help?",
        # ... 3 more
    ],
    "vague": [
        "Tell me about architecture",
        "What's this about?",
        # ... 3 more
    ],
    "specific_technical": [
        "What does Section 7.3.2 say?",
        "TLS encryption requirements?",
        # ... 3 more
    ]
}#
print(f"{'Query':<50} | {'Naive Top':<30} | {'HyDE Top':<30}")
print("-" * 110)

for category, queries in test_queries.items():
    print(f"\n=== {category.upper()} ===")
    for query in queries:
        naive_result = naive_retrieve(query, collection, top_k=1)[0]
        hyde_result = hyde_retrieve(query, collection, top_k=1)[0]
        
        print(f"{query[:48]:<50} | {naive_result[:28]:<30} | {hyde_result[:28]:<30}")
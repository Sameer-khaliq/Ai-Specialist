import sys
import time
from pypdf import PdfReader
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from dotenv import load_dotenv

from ragas import evaluate, EvaluationDataset
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import Faithfulness, ResponseRelevancy, LLMContextRecall

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

def cooldown(seconds: int = 60):
    print("Waiting for API cooldown...")
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rCooldown active: {remaining} seconds remaining... ")
        sys.stdout.flush()
        time.sleep(1)
    print("\rCooldown complete! Resuming code execution.        \n")




def extract_pdf(filepath: str, chunk_size: int = 500) -> list[str]:
    reader = PdfReader(filepath)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    words = full_text.split()
    chunks = []
    current_chunk = []
    current_length = 0

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



def build_dense_index(chunks: list[str]):
    client = chromadb.Client()
    try:
        client.delete_collection("ragas_eval")
    except Exception:
        pass

    collection = client.create_collection("ragas_eval")
    embeds = embeddings_model.embed_documents(chunks)

    collection.add(
        documents=chunks,
        embeddings=embeds,
        ids=[str(i) for i in range(len(chunks))]
    )
    return collection



def retrieve_context(query: str, collection, top_k: int = 5) -> list[str]:
    query_embedding = embeddings_model.embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results["documents"][0]


def generate_answer(query: str, contexts: list[str]) -> str:
    context_text = "\n\n".join(contexts)
    prompt = f"""Answer the question using ONLY the context below.
    If the context does not contain the answer, say "I don't know based on the given context."

    Context:
    {context_text}

    Question: {query}

    Answer:"""
    response = llm.invoke(prompt)
    
        
    
    return response.content
    


test_set = [
    {
        "question": "what is a centralized database",
        "ground_truth": "A centralized database is stored and maintained in a single location, usually a central computer or server, and all users access it through terminals or network connections."
    },
    {
        "question": "what is single tier database architecture",
        "ground_truth": "In a single-tier architecture, the database and user interface exist on the same machine with no separation between client and server, so the user directly interacts with the database without a network connection."
    },
    {
        "question": "what is a distributed database",
        "ground_truth": "A distributed database is spread across multiple computers or sites connected through a network, where each site may hold a portion of the data, and copies may be replicated in different locations for reliability and fault tolerance."
    }
]


if __name__ == "__main__":
    pdf_path = "day11/test.pdf"

    print("PDF load ho rahi hai...")
    chunks = extract_pdf(pdf_path)
    print(f"Total chunks: {len(chunks)}")

    print("\nChromaDB index ban raha hai...")
    collection = build_dense_index(chunks)
    print("Database ready!\n")


    eval_samples = []
    for i, item in enumerate(test_set, start=1):
        query = item["question"]
        print(f"\n{'='*60}\nProcessing {i}/{len(test_set)}: '{query}'\n{'='*60}")

        cooldown(30)
        contexts = retrieve_context(query, collection, top_k=4)

        cooldown(30)
        answer = generate_answer(query, contexts)
        print(f"Generated Answer:\n{answer}\n")

        eval_samples.append({
            "user_input": query,
            "response": answer,
            "retrieved_contexts": contexts,
            "reference": item["ground_truth"],
        })

    print("\nAll samples generated and ready for RAGAS evaluation!")
    print(f"Total evaluation samples: {len(eval_samples)}")
    
    

    # RAGAS stands for "Retrieval-Augmented Generation Assessment Suite". It is a framework for evaluating the performance of retrieval-augmented generation (RAG) systems. RAG systems combine information retrieval techniques with generative models to produce more accurate and contextually relevant responses. The evaluation suite provides metrics and tools to assess the quality of the generated responses, the relevance of the retrieved contexts, and the overall effectiveness of the RAG system in various scenarios.
    # ________________RAGAS Evaluation___________________________
    print("\n" + "="*60)
    print("Running RAGAS evaluation...")
    print("="*60 + "\n")

    evaluation_dataset = EvaluationDataset.from_list(eval_samples)
    evaluator_llm = LangchainLLMWrapper(llm)
    evaluator_embeddings = LangchainEmbeddingsWrapper(embeddings_model)

    from ragas.run_config import RunConfig

    
    config = RunConfig(max_workers=1, timeout=60)

    result = evaluate(
        dataset=evaluation_dataset,
        metrics=[
            Faithfulness(),
            ResponseRelevancy(),
            LLMContextRecall(),
        ],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        run_config=config  
    )
    

    print("\n" + "="*60)
    print("RAGAS SCORECARD")
    print("="*60)
    print(result)

    
    df = result.to_pandas()
    df.to_csv("day11/ragas_scorecard.csv", index=False)
    print("\nScorecard saved to day11/ragas_scorecard.csv")
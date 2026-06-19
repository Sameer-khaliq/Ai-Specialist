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

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")


def cooldown(seconds: int = 60):
    print("Waiting for API cooldown...")
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rCooldown active: {remaining} seconds remaining... ")
        sys.stdout.flush()
        time.sleep(1)
    print("\rCooldown complete! Resuming code execution.        \n")


# ─── STEP 1: PDF chunks (same as Day 8/9/10) ────────────────────────────────

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


# ─── STEP 2: ChromaDB index ──────────────────────────────────────────────────

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


# ─── STEP 3: Naive RAG retrieval + generation ───────────────────────────────

def retrieve_context(query: str, collection, top_k: int = 4) -> list[str]:
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


# ─── STEP 4: Test set — question + ground_truth ─────────────────────────────
# ground_truth manually likha gaya hai PDF content ke hisaab se

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
        "question": "what is three tier database architecture",
        "ground_truth": "In a three-tier architecture, there is an additional middle layer called the application server between the client and the database server, which handles business logic and security before interacting with the database."
    },
    {
        "question": "what is a distributed database",
        "ground_truth": "A distributed database is spread across multiple computers or sites connected through a network, where each site may hold a portion of the data, and copies may be replicated in different locations for reliability and fault tolerance."
    },
    {
        "question": "what is a homogeneous distributed database",
        "ground_truth": "A homogeneous distributed database is one where all sites use the same DBMS software, data structures, and operating system, making the system appear as a single database to the user."
    },
]


# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pdf_path = "day11/test.pdf"

    print("PDF load ho rahi hai...")
    chunks = extract_pdf(pdf_path)
    print(f"Total chunks: {len(chunks)}")

    print("\nChromaDB index ban raha hai...")
    collection = build_dense_index(chunks)
    print("Database ready!\n")

    # Har query ke liye retrieve + generate karke RAGAS-ready samples banao
    eval_samples = []

    for i, item in enumerate(test_set, start=1):
        query = item["question"]
        print(f"\n{'='*60}\nProcessing {i}/{len(test_set)}: '{query}'\n{'='*60}")

        cooldown(30)
        contexts = retrieve_context(query, collection, top_k=2)

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
    print("\nAll samples generated and ready for RAGAS evaluation!")
    print(f"Total evaluation samples: {len(eval_samples)}")
    print("Sample format:")
    for i, sample in enumerate(eval_samples[:3], start=1):
        print(f"  {i}. User Input: {sample['user_input']}")
        print(f"     Response: {sample['response']}")
        print(f"     Retrieved Contexts: {sample['retrieved_contexts']}")
        print(f"     Reference: {sample['reference']}")
    # ─── STEP 5: RAGAS evaluation ────────────────────────────────────────────

    print("\n" + "="*60)
    print("Running RAGAS evaluation...")
    print("="*60 + "\n")

    evaluation_dataset = EvaluationDataset.from_list(eval_samples)

    evaluator_llm = LangchainLLMWrapper(llm)
    evaluator_embeddings = LangchainEmbeddingsWrapper(embeddings_model)

    result = evaluate(
        dataset=evaluation_dataset,
        metrics=[
            Faithfulness(),
            ResponseRelevancy(),
            LLMContextRecall(),
        ],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )

    print("\n" + "="*60)
    print("RAGAS SCORECARD")
    print("="*60)
    print(result)

    # Scorecard ko CSV mein save karo — README/portfolio ke liye useful
    df = result.to_pandas()
    df.to_csv("day11/ragas_scorecard.csv", index=False)
    print("\nScorecard saved to day11/ragas_scorecard.csv")
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from mem0 import Memory
from mem_config import local_mem0_config

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
long_term_memory = Memory.from_config(local_mem0_config)

ENTITY_FILE = "day18/entity_store.json"
short_term_history = []
USER_ID = "sameer_khaliq"

# 2. Entity Memory Helpers (Structured JSON File)
def load_entities() -> dict:
    if os.path.exists(ENTITY_FILE):
        with open(ENTITY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_entities(entities: dict):
    # Ensure directory exists before saving
    os.makedirs(os.path.dirname(ENTITY_FILE), exist_ok=True)
    with open(ENTITY_FILE, "w") as f:
        json.dump(entities, f, indent=4)

def extract_and_update_entities(user_input: str):
    """Asks Gemini to extract explicit key-value facts about the user from the text."""
    current_entities = load_entities()
    
    extraction_prompt = (
        f"Analyze the following text. Extract any permanent personal facts, preferences, or traits "
        f"about the user. Output ONLY a valid, raw JSON object combining these facts with the existing "
        f"known facts: {json.dumps(current_entities)}. Do not include markdown code block syntax. "
        f"Text to analyze: '{user_input}'"
    )
    
    try:
        response = llm.invoke([HumanMessage(content=extraction_prompt)])
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        updated_entities = json.loads(clean_json)
        save_entities(updated_entities)
    except Exception:
        pass

def unified_chat(user_input: str) -> str:
    global short_term_history
    
    # Tier A: Extract entities on the fly
    extract_and_update_entities(user_input)
    current_entities = load_entities()
    
    # Tier B: Semantic long-term lookup from ChromaDB via mem0
    search_results = long_term_memory.search(query=user_input, filters={'user_id': USER_ID})
    
    # Safe fallback parsing for modern Mem0 dictionary structures
    if search_results and isinstance(search_results, list):
        memories = [
            m.get("memory") or m.get("text") or str(m) 
            for m in search_results if isinstance(m, dict)
        ]
        mem0_context = "\n".join(memories)
    else:
        mem0_context = "None"
    
    # Construct System Frame injecting both persistent tiers
    system_instruction = (
        "You are an advanced AI engineer's assistant with a multi-tier memory system.\n\n"
        f"--- LONG TERM RELEVANT CONTEXT ---\n{mem0_context}\n\n"
        f"--- EXTRACTED USER ENTITY FACTS ---\n{json.dumps(current_entities)}\n\n"
        "Use the context and facts naturally if relevant. Be concise and conversational."
    )
    
    # Build complete execution window payload
    messages = [SystemMessage(content=system_instruction)]
    messages.extend(short_term_history[-10:]) # Keep last 10 messages max to avoid bloat
    messages.append(HumanMessage(content=user_input))
    
    # Run Inference
    response = llm.invoke(messages)
    ai_response = response.content
    
    # Tier C: Write back to RAM and long-term vector storage
    short_term_history.append(HumanMessage(content=user_input))
    short_term_history.append(AIMessage(content=ai_response))
    long_term_memory.add(f"User said: {user_input} -> Assistant replied: {ai_response}", user_id=USER_ID)
    
    return ai_response
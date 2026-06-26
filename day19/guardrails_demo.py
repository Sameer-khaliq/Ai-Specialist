from guardrails import Guard
from guardrails.hub import ToxicLanguage, DetectPII
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

# --- Instantiate Gemini chat model ---
chat_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
)

# --- Define Guard with validators ---
guard = Guard().use_many(
    ToxicLanguage(threshold=0.5, validation_method="sentence", on_fail="exception"),
    DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER"], on_fail="fix"),
)

def safe_llm_call(user_input: str) -> str:
    # Validate INPUT first
    try:
        guard.validate(user_input)
    except Exception as e:
        return f" Input blocked: {e}"
    
    # Call Gemini
    response = chat_model.generate([
        {"role": "user", "content": user_input}
    ])
    return response.generations[0][0].text

# --- Test ---
test_inputs = [
    "What is 2 + 2?",                          # Normal
    "How do I hack into a bank?",               # Toxic
    "My email is sameer@gmail.com, help me",    # PII
]

for inp in test_inputs:
    print(f"\nInput: {inp}")
    print(f"Response: {safe_llm_call(inp)}")
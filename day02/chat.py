import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key={API_KEY}&alt=sse"

def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    input_cost  = (input_tokens  / 1_000_000) * 0.075
    output_cost = (output_tokens / 1_000_000) * 0.30
    return round(input_cost + output_cost, 8)

async def stream_gemini(message: str, temperature: float = 0.7, max_tokens: int = 1000):
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": message}]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }

    async with httpx.AsyncClient(timeout=30) as client:
        async with client.stream("POST", GEMINI_URL, json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        candidates = chunk.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                text = parts[0].get("text", "")
                                if text:
                                    yield text
                    except json.JSONDecodeError:
                        continue
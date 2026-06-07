#test raw httpx

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

payload = {
    "contents":[
        {
            "role":"user",
            "parts":[{"text": "Who are you?"}]
        }
    ],
    "generationConfig":{
        "temperature":0.7,
        "maxOutputTokens":100
    }

}
response = httpx.post(URL, json= payload)
data = response.json()

print(data["candidates"][0]["content"]["parts"][0]["text"])
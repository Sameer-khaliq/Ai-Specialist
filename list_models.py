# list_models.py
import httpx
import os
from dotenv import load_dotenv
import pprint

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

# ModelService.ListModels ka raw HTTP endpoint
URL = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

response = httpx.get(URL)
data = response.json()

if "models" in data:
    print("--- AVAILABLE MODELS ON YOUR KEY ---")
    for model in data["models"]:
        print(model["name"])
else:
    print("Error listing models:")
    pprint.pprint(data)
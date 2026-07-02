# runners.py
import time
import ollama
from groq import Groq
from google import genai
import os

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_ollama(model: str, prompt: str):
    start = time.time()
    response = ollama.generate(model=model, prompt=prompt)
    latency = time.time() - start
    return response["response"], latency

def run_groq(prompt: str, model="llama-3.3-70b-versatile"):
    start = time.time()
    response = groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    latency = time.time() - start
    return response.choices[0].message.content, latency

def run_gemini(prompt: str, model="gemini-2.5-flash"):
    start = time.time()
    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt
    )
    latency = time.time() - start
    return response.text, latency
def check_t1(output: str) -> bool:
    return "complaint" in output.lower()

def check_t2(output: str) -> bool:
    return "john carter" in output.lower() and "450" in output

def check_t4(output: str) -> bool:
    return "62" in output
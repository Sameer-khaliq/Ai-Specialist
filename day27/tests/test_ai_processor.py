"""
AI processing service — converts raw form data into a concise, actionable summary.
Uses Groq (Llama-3.3-70B) as the LLM backend.
"""
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.groq_api_key)


def process_form_data(form_data: dict) -> str:
    """
    Takes raw form submission data (dict) and returns a short, human-readable
    summary highlighting the key request, issue, and urgency level.
    """
    prompt = f"""You are processing a customer form submission for a support team.
Summarize the following form data in 2-3 sentences. Clearly state:
1. What the customer's issue or request is
2. The apparent urgency (low, moderate, high)
If the data looks incomplete, malformed, or contains placeholder/template text
instead of real values, explicitly say so instead of guessing.

Form data: {form_data}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content
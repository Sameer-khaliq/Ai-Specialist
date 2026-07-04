from groq import Groq
from app.config import settings

# Groq Client initialize karein (Make sure settings mein exact yahi key variable name ho)
client = Groq(api_key=settings.groq_api_key)

def process_form_data(form_data: dict) -> str:
    prompt = f"""
    You are an advanced triage AI. Analyze the following incoming form submission payload.
    Provide a professional, concise summary (2-3 sentences max).
    Highlight the user's main issue, request, or intent clearly, along with perceived urgency.
    
    Payload Data:
    {form_data}
    """

    # Groq API Call chat completions ke zariye
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2, # Output consistent rakhne ke liye lower temperature behtar hai
    )

    return response.choices[0].message.content.strip()
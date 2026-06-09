import google.genai as genai
from google.genai import types  
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def extract_structured(text: str, schema: type[BaseModel], doc_type: str) -> dict:
    
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1 
    )
    
    prompt = f"""
    Extract structured data from this {doc_type}.
    Return ONLY valid JSON matching this exact schema:
    
    {json.dumps(schema.model_json_schema())}
    
    Document:
    {text}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt,
        config=config
    )
    
    raw_json = json.loads(response.text)
    validated = schema.model_validate(raw_json)
    return validated.model_dump()
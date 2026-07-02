import os
import json
from pydantic import ValidationError
from google import genai
from google.genai import types
from dotenv import load_dotenv
from image_utils import encode_image
from schemas import ExtractionResult

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CLASSIFY_AND_EXTRACT_PROMPT = """
Analyze the document image. Classify it as a "receipt", "diagram", "screenshot", or "other".
Populate the corresponding data field matching that document type inside the schema.
Leave the other type fields null. Do not hallucinate data.
"""

def extract_from_image(image_path: str) -> ExtractionResult:
    b64, mime = encode_image(image_path)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(role="user", parts=[
                types.Part.from_bytes(data=b64, mime_type=mime),
                types.Part.from_text(text=CLASSIFY_AND_EXTRACT_PROMPT)
            ])
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtractionResult, # Now 100% compliant with Developer API
            temperature=0
        )
    )

    return ExtractionResult.model_validate_json(response.text)


def validate_extraction(result: ExtractionResult):
    """Extracts and dumps the active validated sub-model data."""
    # Pull the matching field dynamically based on the classification type
    if result.document_type == "receipt" and result.receipt:
        return result.receipt.model_dump()
    elif result.document_type == "diagram" and result.diagram:
        return result.diagram.model_dump()
    elif result.document_type == "screenshot" and result.screenshot:
        return result.screenshot.model_dump()
        
    return {}
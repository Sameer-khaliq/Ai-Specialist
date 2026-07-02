import gradio as gr
import json
from extractor import extract_from_image, validate_extraction

def process(image):
    if image is None:
        return "Please upload an image."
    result = extract_from_image(image)
    validated = validate_extraction(result)
    output = {
        "document_type": result.document_type,
        "confidence": result.confidence,
        "data": validated
    }
    return json.dumps(output, indent=2)

demo = gr.Interface(
    fn=process,
    inputs=gr.Image(type="filepath", label="Upload receipt / diagram / screenshot"),
    outputs=gr.Code(label="Extracted JSON", language="json"),
    title="Multi-Modal Document Extractor (Gemini Vision)",
    description="Upload any receipt, diagram, or screenshot to get structured JSON output."
)

demo.launch()
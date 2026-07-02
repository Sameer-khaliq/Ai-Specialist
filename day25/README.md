# Day 25 — Multi-Modal Document Extraction Pipeline

## Overview
A vision-powered pipeline that accepts image input (receipts, diagrams, screenshots) and returns clean, structured JSON — no manual data entry required.

Note: Built with Gemini 2.5 Flash (multimodal vision) instead of GPT-4o Vision. Gemini offers native image + JSON-mode support at a lower cost, with comparable extraction accuracy for structured document parsing — a practical swap for production use where API cost matters.

## What it does
- Accepts any image (receipt, diagram, or UI screenshot)
- Classifies the document type automatically
- Extracts type-specific structured data:
  - Receipts: merchant, date, line items, subtotal, tax, total
  - Diagrams: type, title, nodes, relationships, summary
  - Screenshots: app/site, purpose, visible text, key UI elements
- Returns strict, validated JSON (Pydantic-enforced schema)

## Architecture
Image Upload
-> Resize + Base64 Encode (image_utils.py)
-> Gemini 2.5 Flash - Vision + JSON mode (extractor.py)
-> Pydantic Schema Validation (schemas.py)
-> Structured JSON Output

## Tech Stack
- Google Gemini 2.5 Flash (vision + native JSON mode)
- Pydantic v2 (schema validation)
- Gradio (UI)
- Pillow (image preprocessing)

## Results
Tested on 3 distinct image types:

| Image Type      | Detected As | Confidence | Latency   |
|------------------|-------------|------------|-----------|
| Receipt          | receipt     | 0.98       | 4.6s      |
| Flowchart        | diagram     | 1.0        | 9-15s     |
| App Screenshot   | screenshot  | 0.98       | 8-9.4s    |

All three types classified correctly with high confidence. Diagrams take longer due to higher visual complexity (more elements to parse per image).

## Key Engineering Decisions
- Two-tier extraction: classify document type first, then extract type-specific fields, avoids forcing every image into one rigid schema.
- response_mime_type="application/json": forces strict JSON output from Gemini, eliminating markdown-fence stripping hacks.
- Image resizing before encoding: caps token cost without losing text/detail needed for extraction accuracy.
- Pydantic validation layer: catches malformed model output before it reaches the UI, with graceful fallback to raw dict.

## How to run
uv run python day25/extractor.py     (standalone test)
uv run python day25/benchmark.py     (test across all sample images)
uv run python day25/app.py           (Gradio UI)

## Sample Output (Receipt)
{
  "document_type": "receipt",
  "confidence": 0.98,
  "data": {
    "merchant_name": "Your Company Inc.",
    "date": "11-04-2025",
    "line_items": [],
    "subtotal": 240.0,
    "tax": 12.0,
    "total": 252.0,
    "currency": "USD"
  }
}
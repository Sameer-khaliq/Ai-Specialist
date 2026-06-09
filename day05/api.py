from fastapi import FastAPI, HTTPException
from pydantic import BaseModel as PydanticBase
from day05.invoice_extractor import Invoice, SAMPLE_INVOICE
from day05.Contract_extractor import Contract, SAMPLE_CONTRACT
from day05.resume_extractor import Resume, SAMPLE_RESUME
from base_extractor import extract_structured

app = FastAPI(title="Document Extraction API")

class ExtractionRequest(PydanticBase):
    text: str
    doc_type: str  # "invoice", "contract", "resume"

SCHEMA_MAP = {
    "invoice": (Invoice, "invoice"),
    "contract": (Contract, "contract"),
    "resume": (Resume, "resume")
}

@app.post("/extract")
async def extract(request: ExtractionRequest):
    if request.doc_type not in SCHEMA_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"doc_type must be one of: {list(SCHEMA_MAP.keys())}"
        )
    
    schema, doc_type = SCHEMA_MAP[request.doc_type]
    result = extract_structured(request.text, schema, doc_type)
    
    return {
        "doc_type": request.doc_type,
        "extracted_data": result
    }

@app.get("/test/{doc_type}")
async def test_extraction(doc_type: str):
    samples = {
        "invoice": SAMPLE_INVOICE,
        "contract": SAMPLE_CONTRACT,
        "resume": SAMPLE_RESUME
    }
    if doc_type not in samples:
        raise HTTPException(status_code=400, detail="Invalid doc_type")
    
    schema, dtype = SCHEMA_MAP[doc_type]
    result = extract_structured(samples[doc_type], schema, dtype)
    return {"doc_type": doc_type, "extracted_data": result}
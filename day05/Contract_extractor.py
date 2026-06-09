from pydantic import BaseModel, Field
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_extractor import extract_structured

class Party(BaseModel):
    name: str
    role: str  # e.g., "Client", "Contractor"
    address: Optional[str] = None

class KeyClause(BaseModel):
    clause_type: str   # e.g., "Payment", "Termination"
    summary: str
    is_critical: bool

class Contract(BaseModel):
    contract_title: str
    contract_date: str
    effective_date: str
    expiry_date: Optional[str] = None
    parties: list[Party]
    contract_value: Optional[float] = None
    currency: str = "USD"
    payment_terms: str
    key_clauses: list[KeyClause]
    governing_law: Optional[str] = None
    termination_notice_days: Optional[int] = None

SAMPLE_CONTRACT = """
SERVICE AGREEMENT CONTRACT
This Service Agreement ("Agreement") is entered into on January 1, 2025,
effective from February 1, 2025 and expires January 31, 2026.

PARTIES:
- TechSolutions Pvt Ltd ("Contractor"), located at 123 Tech Street, Lahore
- Global Retail Corp ("Client"), located at 456 Market Ave, Dubai

CONTRACT VALUE: $24,000 USD paid monthly at $2,000/month
PAYMENT TERMS: Payment due within 15 days of invoice receipt.

KEY CLAUSES:
1. Confidentiality: Contractor agrees to keep all client data strictly 
   confidential for 3 years after contract termination. CRITICAL.
2. Termination: Either party may terminate with 30 days written notice.
3. Intellectual Property: All work products become property of Client.

Governing Law: Laws of Dubai, UAE
"""

if __name__ == "__main__":
    import json
    print("⏳ Extracting Contract...")
    result = extract_structured(SAMPLE_CONTRACT, Contract, "contract")
    print(json.dumps(result, indent=2))
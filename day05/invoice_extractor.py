from pydantic import BaseModel, Field
from typing import Optional
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_extractor import extract_structured

class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float

class Invoice(BaseModel):
    invoice_number: str
    vendor_name: str
    client_name: str
    issue_date: str
    due_date: Optional[str] = None
    line_items: list[LineItem]
    subtotal: float
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: float
    currency: str = "USD"
    payment_status: str = Field(description="paid, pending, or overdue")

SAMPLE_INVOICE = """
INVOICE #INV-2024-0892
From: TechSolutions Pvt Ltd
To: Global Retail Corp
Issue Date: November 15, 2024
Due Date: December 15, 2024

Services Rendered:
- Website Development (40 hours @ $75/hr) .............. $3,000.00
- UI/UX Design (15 hours @ $60/hr) ..................... $900.00  
- Cloud Setup & Configuration (1 unit @ $500) .......... $500.00
- Monthly Maintenance (1 month @ $200) ................. $200.00

Subtotal: $4,600.00
Tax (10%): $460.00
TOTAL DUE: $5,060.00

Payment Status: PENDING
"""

if __name__ == "__main__":
    import json
    result = extract_structured(SAMPLE_INVOICE, Invoice, "invoice")
    print("Invoice Extracted:")
    print(json.dumps(result, indent=2))
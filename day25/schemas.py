from pydantic import BaseModel
from typing import Literal, Optional

# 1. NEW explicitly defined model to fix the line_items dict issue
class LineItem(BaseModel):
    name: str
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None

class DiagramNode(BaseModel):
    id: str
    text: str
    type: str

class DiagramRelationship(BaseModel):
    source: str
    target: str
    label: Optional[str] = None

class UIElement(BaseModel):
    type: str
    text: str

# 2. Updated ReceiptData using our new LineItem class
class ReceiptData(BaseModel):
    merchant_name: str
    date: Optional[str] = None
    line_items: list[LineItem] = []  # <-- Swapped list[dict] for list[LineItem]
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    currency: Optional[str] = None

class DiagramData(BaseModel):
    diagram_type: str
    title: Optional[str] = None
    nodes: list[DiagramNode]
    relationships: list[DiagramRelationship]
    summary: str

class ScreenshotData(BaseModel):
    app_or_website: Optional[str] = None
    screen_purpose: Optional[str] = None
    visible_text_blocks: list[str] = []
    key_ui_elements: list[UIElement]
    summary: str

class ExtractionResult(BaseModel):
    document_type: Literal["receipt", "diagram", "screenshot", "other"]
    confidence: float
    receipt: Optional[ReceiptData] = None
    diagram: Optional[DiagramData] = None
    screenshot: Optional[ScreenshotData] = None
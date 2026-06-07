#pydantic models
from pydantic import BaseModel
from typing import Optional

class chatmessage(BaseModel):
    role:str
    content:str

class ChatRequest(BaseModel):
    message: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class ChatResponse(BaseModel):
    response: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
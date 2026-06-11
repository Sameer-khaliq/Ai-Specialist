from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from models import ChatRequest
from chat import stream_gemini, calculate_cost

app = FastAPI(title="AI Chat API", version="1.0.0")

@app.get("/")
def root():
    return {"status": "running", "day": 2}

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    async def generate():
        try:
            async for token in stream_gemini(
                message=request.message,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                yield token
        except Exception as e:
            yield f"\n[Error: {str(e)}]"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )

@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    full_response = ""
    try:
        async for token in stream_gemini(
            message=request.message,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        ):
            full_response += token
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Rough token estimation
    input_tokens  = len(request.message.split()) * 1.3
    output_tokens = len(full_response.split()) * 1.3
    cost = calculate_cost(int(input_tokens), int(output_tokens))
    
    return {
        "response": full_response,
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "cost_usd": cost,
        "model": "gemini-1.5-flash"
    }
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
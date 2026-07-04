from fastapi import FastAPI
from app.routes.webhook import router as webhook_router
from app.core.logging_config import setup_logging


setup_logging()

app = FastAPI(
    title="Production AI Webhook Pipeline", 
    version="1.0.0",
    description="Asynchronous automated AI orchestration via FastAPI & Gemini"
)


app.include_router(webhook_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": "running"}
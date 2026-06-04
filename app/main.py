from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME
)

@app.get("/")
def root():
    return {
        "message": "AI Agent Platform is running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
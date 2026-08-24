from fastapi import FastAPI
from app.api import auth, messages, users, agents, chats
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(agents.router)
app.include_router(chats.router)
app.include_router(messages.router)

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
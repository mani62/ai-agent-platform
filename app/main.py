from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.ai.tools.setup import register_tools
from app.api import auth, messages, users, agents, chats
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.tool_service import ToolService

@asynccontextmanager
async def lifespan(app: FastAPI):
    register_tools()

    db = SessionLocal()

    try:
        ToolService().sync_tools(db)
    finally:
        db.close()

    yield
    
app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
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
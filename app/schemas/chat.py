from pydantic import BaseModel, ConfigDict
from app.schemas.base import BaseResponse

class ChatCreate(BaseModel):
    agent_uuid: str

class ChatResponse(BaseResponse):
    uuid: str
    title: str | None

    model_config = ConfigDict(from_attributes=True)

class ChatUpdate(BaseModel):
    title: str | None = None    
 
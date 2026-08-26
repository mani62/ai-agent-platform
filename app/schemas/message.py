from pydantic import BaseModel

from app.schemas.base import BaseResponse
from app.core.enums import MessageRole

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseResponse):
    uuid: str
    role: MessageRole
    content: str
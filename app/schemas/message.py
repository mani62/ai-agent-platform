from pydantic import BaseModel

from app.schemas.base import BaseResponse

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseResponse):
    uuid: str
    role: str
    content: str
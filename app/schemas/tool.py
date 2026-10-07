from uuid import UUID
from app.schemas.base import BaseResponse

class ToolRead(BaseResponse):
    uuid: UUID
    name: str
    description: str
    is_active: bool
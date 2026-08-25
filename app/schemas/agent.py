from typing import Literal
from pydantic import BaseModel, Field
from app.schemas.base import BaseResponse

class AgentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    system_prompt: str = Field(min_length=1)
    provider: Literal["ollama", "openai"] = "ollama"
    model: str = Field(min_length=1, max_length=100)
class AgentUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    system_prompt: str | None = Field(
        default=None,
        min_length=1,
    )

    model: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    provider: Literal["ollama", "openai"] | None = None

    is_active: bool | None = None
    
class AgentRead(BaseResponse):
    uuid: str
    name: str
    description: str | None
    system_prompt: str
    provider: str
    model: str
    is_active: bool
    

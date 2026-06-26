from pydantic import BaseModel

class AgentCreate(BaseModel):
    name: str
    description: str | None = None
    system_prompt: str
    model: str = "gpt-4.1-mini"

class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    model: str | None = None
    is_active: bool | None = None

class AgentRead(BaseModel):
    uuid: str
    name: str
    description: str | None
    system_prompt: str
    model: str
    is_active: bool

    class Config:
        from_attributes = True
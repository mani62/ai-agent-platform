from datetime import datetime

from pydantic import BaseModel, ConfigDict

class BaseResponse(BaseModel):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
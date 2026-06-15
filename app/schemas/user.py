from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    uuid: str
    first_name: str
    last_name: str   
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        from_attributes = True
 
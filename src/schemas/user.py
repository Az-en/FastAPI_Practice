from pydantic import BaseModel
import uuid
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    role : str

class UserResponse(UserBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class UserLoginResponse(UserResponse):
    successful_login: bool
    token: str

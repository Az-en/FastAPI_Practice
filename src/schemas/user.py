from pydantic import BaseModel
import uuid
import enum
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    role : str

class UserResponse(UserBase):
    id: uuid.UUID
    role: str | None
    class Config:
        from_attributes = True
    

class UserLogin(BaseModel):
    email: str
    password: str

class UserLoginResponse(UserResponse):
    token: str

class UserRole(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"
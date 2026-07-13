import enum
import uuid
from sqlalchemy import Column, Uuid, String, Enum
from src.core.database import Base


class UserRole(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"
class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True,default=uuid.uuid4, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String,nullable=False)
    role = Column(Enum(UserRole),nullable=True)
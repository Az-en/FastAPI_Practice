from src.core.database import Base
import uuid
from sqlalchemy import Column, Uuid, String, Text, ForeignKey

# TODO: Later
class CourseToUser(Base):
    __tablename__ = ""
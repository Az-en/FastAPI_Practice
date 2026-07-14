from src.core.database import Base
import uuid
from sqlalchemy import Column, Uuid, String, Text, ForeignKey
class Course(Base):
    __tablename__ = "courses"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)

    title = Column(String(100), nullable=False) # String with length constraint
    course_code = Column(String(20), unique=True, index=True, nullable=False) # e.g., "CS-101"
    description = Column(Text, nullable=True)     
    instructor_id = Column(Uuid, ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
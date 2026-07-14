from src.models.course import Course
from src.schemas.course import CourseCreate
from sqlalchemy.orm import Session
class CourseRepository:
    
    def __init__(self,session: Session):
        self.session = session
    
    def create_course(self,course_in:CourseCreate):
        course = Course(**course_in.model_dump())   # converting from a pydantic class to a sqlAlchemy ORM model
        self.session.add(course)
        self.session.commit()
        self.session.refresh(course)
        return course
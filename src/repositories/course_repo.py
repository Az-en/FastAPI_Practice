from uuid import UUID
from src.models.course import Course
from src.schemas.course import CourseCreate, CourseUpdate
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

    def get_course(self, course_id: UUID):
        return self.session.query(Course).filter(Course.id == course_id).first()

    def get_all_courses(self):
        return self.session.query(Course).all()

    def update_course(self, course_id: UUID, course_in: CourseUpdate):
        course = self.get_course(course_id)
        if not course:
            return None

        update_data = course_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        self.session.commit()
        self.session.refresh(course)
        return course

    def delete_course(self, course_id: UUID):
        course = self.get_course(course_id)
        if not course:
            return False

        self.session.delete(course)
        self.session.commit()
        return True
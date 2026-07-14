from pydantic import BaseModel
import uuid

class Course(BaseModel):
    title: str
    course_code: str
    description: str

class CourseCreate(Course):
    instructor_id: uuid.UUID

class CourseResponse(Course):
    id: uuid.UUID
    instructor_id: uuid.UUID
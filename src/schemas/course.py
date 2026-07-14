from pydantic import BaseModel
import uuid

class Course(BaseModel):
    title: str
    course_code: str
    description: str | None = None

class CourseCreate(Course):
    instructor_id: uuid.UUID


class CourseUpdate(BaseModel):
    title: str | None = None
    course_code: str | None = None
    description: str | None = None
    instructor_id: uuid.UUID | None = None

class CourseResponse(Course):
    id: uuid.UUID
    instructor_id: uuid.UUID

    class Config:
        from_attributes = True
from uuid import UUID
from src.schemas.course import CourseCreate
from src.repositories.user_repo import UserRepository
from src.repositories.course_repo import CourseRepository
from fastapi import HTTPException,status
class CourseService:
    def __init__(self,user_repo: UserRepository, course_repo: CourseRepository):
        self.user_repo = user_repo
        self.course_repo = course_repo

    def create_course(self,course:CourseCreate):
        user = self.user_repo.get_user(course.instructor_id)

        if user.role.lower() != "teacher":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {course.instructor_id} is not a valid instructor."
            )

        return self.course_repo.create_course(course_in=course)
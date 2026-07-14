from uuid import UUID
from src.schemas.course import CourseCreate, CourseUpdate
from src.repositories.user_repo import UserRepository
from src.repositories.course_repo import CourseRepository
from fastapi import HTTPException,status


class CourseService:
    def __init__(self,user_repo: UserRepository, course_repo: CourseRepository):
        self.user_repo = user_repo
        self.course_repo = course_repo

    def _ensure_instructor(self, instructor_id: UUID):
        user = self.user_repo.get_user(instructor_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {instructor_id} was not found.",
            )

        role = getattr(user.role, "value", user.role)
        if str(role).lower() != "teacher":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {instructor_id} is not a valid instructor.",
            )

        return user

    def create_course(self,course:CourseCreate):
        self._ensure_instructor(course.instructor_id)
        return self.course_repo.create_course(course_in=course)

    def get_course(self, course_id: UUID):
        return self.course_repo.get_course(course_id)

    def get_all_courses(self):
        return self.course_repo.get_all_courses()

    def update_course(self, course_id: UUID, course_in: CourseUpdate):
        if course_in.instructor_id is not None:
            self._ensure_instructor(course_in.instructor_id)

        return self.course_repo.update_course(course_id=course_id, course_in=course_in)

    def delete_course(self, course_id: UUID):
        return self.course_repo.delete_course(course_id)
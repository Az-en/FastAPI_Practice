from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.dependencies import get_db, get_current_user,get_teacher_user
from src.schemas.course import CourseResponse, CourseCreate, CourseUpdate
from src.repositories.course_repo import CourseRepository
from src.repositories.user_repo import UserRepository
from src.services.course_service import CourseService
from src.models.course import Course


courseRouter = APIRouter(prefix="/courses", tags=["Courses"], dependencies=[Depends(get_current_user)])


def _serialize_course(course: Course | dict) -> dict:
    if isinstance(course, dict):
        return dict(course)

    return {
        "id": course.id,
        "title": course.title,
        "course_code": course.course_code,
        "description": course.description,
        "instructor_id": course.instructor_id,
    }

@courseRouter.post("/",response_model=CourseResponse)
def create_course(course_in:CourseCreate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    course_repo = CourseRepository(db)
    ser = CourseService(user_repo=user_repo,course_repo=course_repo)
    created_course = ser.create_course(course=course_in)
    if not created_course:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to create course")
    
    return created_course


@courseRouter.get("/", response_model=list[CourseResponse])
def get_all_courses(db: Session = Depends(get_db),current_user = Depends(get_teacher_user)):
    user_repo = UserRepository(db)
    course_repo = CourseRepository(db)
    ser = CourseService(user_repo=user_repo, course_repo=course_repo)
    courses = ser.get_all_courses()

    if not courses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Courses not found")

    return [_serialize_course(course) for course in courses]


@courseRouter.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: UUID, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    course_repo = CourseRepository(db)
    ser = CourseService(user_repo=user_repo, course_repo=course_repo)
    course = ser.get_course(course_id)

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    return _serialize_course(course)


@courseRouter.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: UUID, course_in: CourseUpdate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    course_repo = CourseRepository(db)
    ser = CourseService(user_repo=user_repo, course_repo=course_repo)
    updated_course = ser.update_course(course_id, course_in)

    if not updated_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    return _serialize_course(updated_course)


@courseRouter.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: UUID, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    course_repo = CourseRepository(db)
    ser = CourseService(user_repo=user_repo, course_repo=course_repo)
    deleted = ser.delete_course(course_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    return None


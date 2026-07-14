from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.dependencies import get_db, get_current_user
from src.schemas.course import CourseResponse,CourseCreate
from src.repositories.course_repo import CourseRepository
from src.repositories.user_repo import UserRepository
from src.services.course_service import CourseService
courseRouter = APIRouter(prefix="/courses",tags=['Courses'],dependencies=[Depends(get_current_user)],)

@courseRouter.post("/",response_model=CourseResponse)
def create_course(course_in:CourseCreate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    course_repo = CourseRepository(db)
    ser = CourseService(user_repo=user_repo,course_repo=course_repo)
    created_course = ser.create_course(course=course_in)
    if not created_course:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to create course")
    
    return created_course


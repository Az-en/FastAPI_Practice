from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.dependencies import get_db, get_current_user
from src.schemas.course import CourseResponse,CourseCreate
from src.repositories.course_repo import CourseRepository
courseRouter = APIRouter(prefix="/courses",tags=['Courses'],dependencies=[Depends(get_current_user)],)

@courseRouter.post("/",response_model=CourseResponse)
def create_course(course:CourseCreate, db: Session = Depends(get_db)):
    repo = CourseRepository(db)
    created_course = repo.create_course(course_in=course)
    if not created_course:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to create course")
    
    return created_course


import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.dependencies import get_db, get_current_user
from src.schemas.user import UserCreate, UserResponse, UserLogin, UserLoginResponse
from src.repositories.user_repo import UserRepository
from src.core.security import create_jwt, verify_password, JWTPayload
from src.models.user import User
userRouter = APIRouter(prefix="/users", tags=["Users"],)

@userRouter.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    return repo.create_user(user)

@userRouter.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: uuid.UUID, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    repo = UserRepository(db)
    user = repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@userRouter.post("/login",response_model=UserLoginResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    repo = UserRepository(db)

    user = repo.get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    verified_password = verify_password(credentials.password,user.password)
    if not verified_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    jwt_payload = JWTPayload(id=user.id,role=user.role)
    token = create_jwt(jwt_payload)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "successful_login": True,
        "token": token
    }

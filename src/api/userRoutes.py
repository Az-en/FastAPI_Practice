import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import StatementError
from src.api.dependencies import get_db, get_current_user
from src.schemas.user import UserCreate, UserResponse, UserLogin, UserLoginResponse
from src.repositories.user_repo import UserRepository
from src.core.security import create_jwt, verify_password, JWTPayload
from src.models.user import User
userRouter = APIRouter(prefix="/users", tags=["Users"],)

_VALID_ROLES = {"teacher", "student"}


def _serialize_user(user: User | dict) -> dict:
    if isinstance(user, dict):
        user_data = dict(user)
    else:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }

    role_value = getattr(user_data.get("role"), "value", user_data.get("role"))
    if isinstance(role_value, str):
        role_value = role_value.lower()

    user_data["role"] = role_value if role_value in _VALID_ROLES else None
    return user_data

@userRouter.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    try:
        return _serialize_user(repo.create_user(user))
    except (LookupError, StatementError, ValueError):
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid role. Allowed values are teacher and student.",
        )

@userRouter.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: uuid.UUID, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    repo = UserRepository(db)
    user = repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _serialize_user(user)

@userRouter.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = UserRepository(db)
    users = repo.get_all_users()

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")

    return [_serialize_user(user) for user in users]

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
    jwt_payload = JWTPayload(id=user.id, role=user.role)
    token = create_jwt(jwt_payload)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "token": token,
        "role": _serialize_user(user)["role"]
    }

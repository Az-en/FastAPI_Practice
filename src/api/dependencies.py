from src.core.database import SessionLocal
from src.models.user import User
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from src.repositories.user_repo import UserRepository
from src.core.security import decode_jwt
import logging
logger = logging.getLogger(__name__)

oauth2_scheme = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_jwt(token.credentials)
        user_id = payload.id
        logger.info("Authenticated user id=%s", user_id)
        if user_id is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    # Fetch the user from the database
    repo = UserRepository(db)
    user = repo.get_user(user_id)
    if user is None:
        raise credentials_exception
        
    return user
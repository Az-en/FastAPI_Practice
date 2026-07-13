from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserCreate

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user_in: UserCreate) -> User:
        db_user = User(**user_in.model_dump())
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user
    
    def get_user(self, user_id: int) -> User | None:
        return self.session.query(User).filter(User.id == user_id).first()
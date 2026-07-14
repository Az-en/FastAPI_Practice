import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserCreate
from src.core.security import hash_password

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user_in: UserCreate) -> User:
        db_user = User(**user_in.model_dump())
        self.session.add(db_user)
        db_user.password = hash_password(db_user.password)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user
    
    def get_user(self, user_id: uuid.UUID) -> User | None:
        return self.session.query(User).filter(User.id == user_id).first()
    
    def get_all_users(self) -> User | None:
        query = text("SELECT * FROM users;")
        result = self.session.execute(query)
        return result.mappings().all()
    
    def get_user_by_email(self, user_email: str) -> User | None:
        return self.session.query(User).filter(User.email == user_email).first()
    
    def delete_user(self,user_id: uuid.UUID):
        user = self.session.query(User).filter(User.id == user_id).first()

        if not user:
            return False
        self.session.delete(user)
        self.session.commit()
        
        return True

if __name__ == "__main__":
    from src.core.database import SessionLocal
    import uuid

    # 1. Create a real database session
    db = SessionLocal()
    
    try:
        repo = UserRepository(db)
        
        
        result = repo.get_all_users()
        print(f"{result}")
        
    finally:
        # 3. Always close the session when done
        db.close()
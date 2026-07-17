import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from src.core.database import Base
from src.api.dependencies import get_db
from src.main import app

from src.models import user,course

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture()
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(autoflush=False, bind=engine,autocommit = False)
    session = TestSessionLocal()
    print(engine.url)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def teacher_user(db_session):
    from src.repositories.user_repo import UserRepository
    from src.schemas.user import UserCreate
    from src.schemas.user import UserRole

    repo = UserRepository(db_session)
    return repo.create_user(UserCreate(
        username="prof_hint",
        email="prof@example.com",
        password="hunter22",
        role=UserRole.TEACHER,
    ))


@pytest.fixture()
def auth_headers(client, teacher_user):
    response = client.post("/users/login", json={
        "email": "prof@example.com",
        "password": "hunter22",
    })
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
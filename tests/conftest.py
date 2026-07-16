from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models.user import User

from app.models.agent import Agent

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

@pytest.fixture
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client(
    db: Session,
) -> Generator[TestClient, None, None]:

    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def test_user(
    db: Session,
) -> User:
    user = User(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        hashed_password=hash_password("StrongPassword123!"),
        is_active=True,
        is_verified=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@pytest.fixture
def auth_headers(
    client: TestClient,
    test_user: User,
) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }

@pytest.fixture
def test_agent(
    db: Session,
    test_user: User,
) -> Agent:
    agent = Agent(
        user_id=test_user.id,
        name="Test Agent",
        description="Agent used for testing",
        system_prompt="You are a test assistant.",
        model="gpt-4.1-mini",
        is_active=False,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent

@pytest.fixture
def second_user(
    db: Session,
) -> User:
    user = User(
        first_name="Second",
        last_name="User",
        email="second@example.com",
        hashed_password=hash_password("StrongPassword123!"),
        is_active=True,
        is_verified=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
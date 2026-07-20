import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Import ALL models so Base.metadata discovers them
import app.models  # noqa: F401

from app.auth.models import User
from app.auth.service import create_access_token, hash_password
from app.database.database import Base, get_db
from app.main import app

# Use shared in-memory SQLite
TEST_DATABASE_URL = "sqlite:///file::memory:?cache=shared&uri=true"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test, drop them after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def override_get_db():
    """FastAPI dependency override that uses the test database."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def db() -> Session:
    """Provide a fresh database session for direct service calls."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    """Provide a TestClient with the test database dependency."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user_data():
    """Return test user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
    }


@pytest.fixture()
def test_user(db) -> User:
    """Create a test user directly in the database."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password("password123"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def auth_headers(test_user) -> dict:
    """Return Authorization headers for the test user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def registered_client(client, test_user_data):
    """Register a user via API and return the client."""
    client.post("/auth/register", json=test_user_data)
    resp = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    })
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture()
def workspace(db, test_user):
    """Create a test workspace."""
    from app.workspaces.models import Workspace
    ws = Workspace(name="Test Workspace", owner_id=test_user.id)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws


@pytest.fixture()
def workflow(db, workspace):
    """Create a test workflow."""
    from app.workflows.models import Workflow
    wf = Workflow(
        workspace_id=workspace.id,
        name="Test Workflow",
        description="A test workflow",
        status="draft",
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf

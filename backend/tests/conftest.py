"""Test fixtures for Discovery backend."""

import os

# Override DATABASE_URL BEFORE any app imports
os.environ["DATABASE_URL"] = "sqlite://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.mixins import generate_uuid  # noqa: E402
from app.models.tenant import Tenant  # noqa: E402
from app.models.user import User  # noqa: E402
from app.core.security import get_password_hash, create_access_token  # noqa: E402

# Test engine — SQLite in-memory with StaticPool so all connections share one DB
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():
    """Get a test database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """FastAPI test client with DB override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_tenant(db):
    """Create a test tenant."""
    tenant = Tenant(id=generate_uuid(), name="Test Lab", slug="test-lab")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@pytest.fixture
def test_user(db, test_tenant):
    """Create a test user."""
    user = User(
        id=generate_uuid(),
        email="scientist@testlab.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test Scientist",
        role="admin",
        is_active=True,
        tenant_id=test_tenant.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user, test_tenant):
    """Get auth headers with a valid JWT."""
    token = create_access_token(
        data={"sub": test_user.email, "tenant_id": test_tenant.id}
    )
    return {"Authorization": f"Bearer {token}"}

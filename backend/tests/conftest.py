import os
from pathlib import Path

# Test settings must be configured before importing the FastAPI app.
TEST_DATABASE_PATH = Path(__file__).resolve().parent / "test_chatbot.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE_PATH.as_posix()}"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_EMAIL"] = "admin@example.com"
os.environ["ADMIN_PASSWORD"] = "Admin123!"
os.environ["ADMIN_SECRET_KEY"] = "stage-6-test-secret-key"
os.environ["ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES"] = "120"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.migrations import run_lightweight_migrations
from app.seed import seed_database


@pytest.fixture(autouse=True)
def reset_database():
    """Give every test a clean, seeded SQLite database."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    run_lightweight_migrations()
    seed_database()
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_token(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "Admin123!"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

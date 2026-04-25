import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_and_login():
    # Register
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "secret123",
        "full_name": "Test User",
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

    # Login
    response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "secret123",
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    # Get me
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_task_crud():
    # Login
    login = client.post("/api/v1/auth/login", data={"username": "testuser", "password": "secret123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    response = client.post("/api/v1/tasks", json={
        "title": "Test Task",
        "description": "Do something important",
        "priority": "high",
    }, headers=headers)
    assert response.status_code == 201
    task_id = response.json()["id"]

    # Get
    response = client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"

    # Update
    response = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "in_progress"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"

    # Delete
    response = client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
    assert response.status_code == 204

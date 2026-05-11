import os

os.environ["DATABASE_URL"] = "sqlite:///./test_task_tracker.db"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-bytes"

from fastapi.testclient import TestClient

from app.models import Base
from app.core.db import engine
from main import app


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module() -> None:
    Base.metadata.drop_all(bind=engine)


def register_and_login(client: TestClient, email: str = "fox@example.com", username: str = "fox") -> None:
    response = client.post(
        "/auth/register",
        data={"email": email, "username": username, "password": "secret123"},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_register_create_task_move_and_pomodoro_session() -> None:
    with TestClient(app) as client:
        register_and_login(client)

        task_response = client.post(
            "/api/tasks",
            json={
                "title": "Write portfolio app",
                "description": "Build the MVP",
                "status": "todo",
                "priority": "high",
                "deadline": None,
                "tags": ["portfolio", "fastapi"],
            },
        )
        assert task_response.status_code == 201
        task = task_response.json()
        assert task["title"] == "Write portfolio app"

        move_response = client.post(
            f"/tasks/{task['id']}/status",
            data={"status": "in_progress", "position": 1},
        )
        assert move_response.status_code == 204

        session_response = client.post(
            "/pomodoro/sessions",
            data={"task_id": task["id"], "session_type": "work", "duration_minutes": 25},
        )
        assert session_response.status_code == 200
        assert session_response.json()["completed"] is True

        dashboard_session_response = client.post(
            "/pomodoro/sessions/html",
            data={"task_id": task["id"], "session_type": "work", "duration_minutes": 25},
            follow_redirects=False,
        )
        assert dashboard_session_response.status_code == 303


def test_auth_pages_render() -> None:
    with TestClient(app) as client:
        login_response = client.get("/auth/login")
        register_response = client.get("/auth/register")

        assert login_response.status_code == 200
        assert "Вход" in login_response.text
        assert register_response.status_code == 200
        assert "Регистрация" in register_response.text


def test_user_cannot_access_other_users_task() -> None:
    with TestClient(app) as client:
        register_and_login(client)
        task_response = client.post("/api/tasks", json={"title": "Private task"})
        task_id = task_response.json()["id"]
        client.cookies.clear()
        register_and_login(client, email="other@example.com", username="other")
        forbidden = client.get(f"/api/tasks/{task_id}")
        assert forbidden.status_code == 404


import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import main
import models
from database import Base


# ---------------- ISOLATED TEST DATABASE ----------------

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


# ---------------- DATABASE DEPENDENCY OVERRIDE ----------------

def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


# ---------------- TEST FIXTURE ----------------

@pytest.fixture
def client():

    # Create a clean database for every test
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    main.app.dependency_overrides[main.get_db] = override_get_db

    try:
        with TestClient(main.app) as test_client:
            yield test_client

    finally:
        main.app.dependency_overrides.pop(main.get_db, None)
        Base.metadata.drop_all(bind=test_engine)


# ---------------- CREATE TESTS ----------------

def test_create_brief(client):

    response = client.post(
        "/briefs",
        json={
            "title": "Test Website",
            "description": "Build a website for a client"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Test Website"
    assert data["description"] == "Build a website for a client"
    assert "id" in data


def test_create_brief_with_exactly_100_character_title(client):

    response = client.post(
        "/briefs",
        json={
            "title": "A" * 100,
            "description": "Valid description"
        }
    )

    assert response.status_code == 201
    assert len(response.json()["title"]) == 100


def test_create_brief_with_empty_title(client):

    response = client.post(
        "/briefs",
        json={
            "title": "",
            "description": "Build a website"
        }
    )

    assert response.status_code == 422


def test_create_brief_with_whitespace_title(client):

    response = client.post(
        "/briefs",
        json={
            "title": "   ",
            "description": "Build a website"
        }
    )

    assert response.status_code == 422


def test_create_brief_with_empty_description(client):

    response = client.post(
        "/briefs",
        json={
            "title": "Valid Project",
            "description": ""
        }
    )

    assert response.status_code == 422


def test_create_brief_with_whitespace_description(client):

    response = client.post(
        "/briefs",
        json={
            "title": "Valid Project",
            "description": "   "
        }
    )

    assert response.status_code == 422


def test_create_brief_with_long_title(client):

    response = client.post(
        "/briefs",
        json={
            "title": "A" * 101,
            "description": "Build a website"
        }
    )

    assert response.status_code == 422


def test_create_brief_with_long_description(client):

    response = client.post(
        "/briefs",
        json={
            "title": "AgencyOS",
            "description": "A" * 1001
        }
    )

    assert response.status_code == 422


def test_create_brief_trims_whitespace(client):

    response = client.post(
        "/briefs",
        json={
            "title": "  AgencyOS  ",
            "description": "  Build a website  "
        }
    )

    assert response.status_code == 201
    assert response.json()["title"] == "AgencyOS"
    assert response.json()["description"] == "Build a website"


def test_create_brief_rejects_integer_title(client):

    response = client.post(
        "/briefs",
        json={
            "title": 12345,
            "description": "Build a website"
        }
    )

    assert response.status_code == 422


# ---------------- READ TESTS ----------------

def test_get_all_briefs(client):

    client.post(
        "/briefs",
        json={
            "title": "Hospital Website",
            "description": "Build a hospital website"
        }
    )

    response = client.get("/briefs")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Hospital Website"


def test_get_one_brief(client):

    create_response = client.post(
        "/briefs",
        json={
            "title": "E-commerce Website",
            "description": "Build an online shopping website"
        }
    )

    brief_id = create_response.json()["id"]

    response = client.get(f"/briefs/{brief_id}")

    assert response.status_code == 200
    assert response.json()["id"] == brief_id
    assert response.json()["title"] == "E-commerce Website"


def test_get_missing_brief(client):

    response = client.get("/briefs/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Brief not found"


# ---------------- UPDATE TESTS ----------------

def test_update_brief(client):

    create_response = client.post(
        "/briefs",
        json={
            "title": "Old Website",
            "description": "Original description"
        }
    )

    brief_id = create_response.json()["id"]

    response = client.put(
        f"/briefs/{brief_id}",
        json={
            "title": "Updated Website",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Brief updated successfully"
    assert data["brief"]["title"] == "Updated Website"
    assert data["brief"]["description"] == "Updated description"


def test_update_missing_brief(client):

    response = client.put(
        "/briefs/999",
        json={
            "title": "Updated Website",
            "description": "Updated description"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Brief not found"


# ---------------- DELETE TESTS ----------------

def test_delete_brief(client):

    create_response = client.post(
        "/briefs",
        json={
            "title": "Portfolio Website",
            "description": "Build a portfolio website"
        }
    )

    brief_id = create_response.json()["id"]

    response = client.delete(f"/briefs/{brief_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Brief deleted successfully"
    assert response.json()["brief"]["id"] == brief_id

    get_response = client.get(f"/briefs/{brief_id}")

    assert get_response.status_code == 404


def test_delete_missing_brief(client):

    response = client.delete("/briefs/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Brief not found"

# ---------------- TASK TEST HELPERS ----------------

def create_test_brief(client, title="Test Brief"):
    response = client.post(
        "/briefs",
        json={
            "title": title,
            "description": "A brief for testing tasks"
        }
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_test_task(client, brief_id, title="Test Task"):
    return client.post(
        f"/briefs/{brief_id}/tasks",
        json={
            "title": title,
            "description": "A task for testing"
        }
    )


# ---------------- TASK CREATE TESTS ----------------

def test_create_task(client):
    brief_id = create_test_brief(client)

    response = create_test_task(client, brief_id)

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Test Task"
    assert data["description"] == "A task for testing"
    assert data["status"] == "todo"
    assert data["brief_id"] == brief_id
    assert "id" in data


def test_create_task_under_missing_brief(client):
    response = create_test_task(client, 999)

    assert response.status_code == 404
    assert response.json()["detail"] == "Brief not found"


def test_create_task_with_whitespace_title(client):
    brief_id = create_test_brief(client)

    response = client.post(
        f"/briefs/{brief_id}/tasks",
        json={
            "title": "   ",
            "description": "Valid description"
        }
    )

    assert response.status_code == 422


def test_create_task_with_long_title(client):
    brief_id = create_test_brief(client)

    response = client.post(
        f"/briefs/{brief_id}/tasks",
        json={
            "title": "A" * 101,
            "description": "Valid description"
        }
    )

    assert response.status_code == 422


def test_create_task_with_long_description(client):
    brief_id = create_test_brief(client)

    response = client.post(
        f"/briefs/{brief_id}/tasks",
        json={
            "title": "Valid Task",
            "description": "A" * 1001
        }
    )

    assert response.status_code == 422


# ---------------- TASK READ TESTS ----------------

def test_get_all_tasks_under_brief(client):
    brief_id = create_test_brief(client)

    create_test_task(client, brief_id, "Task One")
    create_test_task(client, brief_id, "Task Two")

    response = client.get(f"/briefs/{brief_id}/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Task One"
    assert response.json()[1]["title"] == "Task Two"


def test_get_tasks_only_for_requested_brief(client):
    first_brief_id = create_test_brief(client, "First Brief")
    second_brief_id = create_test_brief(client, "Second Brief")

    create_test_task(client, first_brief_id, "First Task")
    create_test_task(client, second_brief_id, "Second Task")

    response = client.get(f"/briefs/{first_brief_id}/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "First Task"


def test_get_tasks_under_missing_brief(client):
    response = client.get("/briefs/999/tasks")

    assert response.status_code == 404
    assert response.json()["detail"] == "Brief not found"


def test_get_one_task(client):
    brief_id = create_test_brief(client)
    create_response = create_test_task(client, brief_id)

    task_id = create_response.json()["id"]

    response = client.get(
        f"/briefs/{brief_id}/tasks/{task_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Test Task"


def test_get_missing_task(client):
    brief_id = create_test_brief(client)

    response = client.get(
        f"/briefs/{brief_id}/tasks/999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_get_task_from_wrong_brief(client):
    first_brief_id = create_test_brief(client, "First Brief")
    second_brief_id = create_test_brief(client, "Second Brief")

    task_response = create_test_task(
        client, first_brief_id
    )

    task_id = task_response.json()["id"]

    response = client.get(
        f"/briefs/{second_brief_id}/tasks/{task_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


# ---------------- TASK UPDATE TESTS ----------------

def test_update_task(client):
    brief_id = create_test_brief(client)
    create_response = create_test_task(client, brief_id)

    task_id = create_response.json()["id"]

    response = client.put(
        f"/briefs/{brief_id}/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "description": "Updated task description",
            "status": "in_progress"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated task description"
    assert data["status"] == "in_progress"


def test_update_task_status_to_done(client):
    brief_id = create_test_brief(client)
    task_id = create_test_task(
        client, brief_id
    ).json()["id"]

    response = client.put(
        f"/briefs/{brief_id}/tasks/{task_id}",
        json={
            "title": "Completed Task",
            "description": "Task completed successfully",
            "status": "done"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_update_task_with_invalid_status(client):
    brief_id = create_test_brief(client)
    task_id = create_test_task(
        client, brief_id
    ).json()["id"]

    response = client.put(
        f"/briefs/{brief_id}/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "description": "Updated description",
            "status": "invalid_status"
        }
    )

    assert response.status_code == 422


def test_update_missing_task(client):
    brief_id = create_test_brief(client)

    response = client.put(
        f"/briefs/{brief_id}/tasks/999",
        json={
            "title": "Updated Task",
            "description": "Updated description",
            "status": "done"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


# ---------------- TASK DELETE TESTS ----------------

def test_delete_task(client):
    brief_id = create_test_brief(client)
    create_response = create_test_task(client, brief_id)

    task_id = create_response.json()["id"]

    response = client.delete(
        f"/briefs/{brief_id}/tasks/{task_id}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"
    assert response.json()["task"]["id"] == task_id

    get_response = client.get(
        f"/briefs/{brief_id}/tasks/{task_id}"
    )

    assert get_response.status_code == 404


def test_delete_missing_task(client):
    brief_id = create_test_brief(client)

    response = client.delete(
        f"/briefs/{brief_id}/tasks/999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

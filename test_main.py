
import pytest
import main

from fastapi.testclient import TestClient

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_briefs():
    main.briefs.clear()
    main.next_id = 1


def test_create_brief():

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


def test_get_all_briefs():

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


def test_get_one_brief():

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


def test_get_missing_brief():

    response = client.get("/briefs/999")


    assert response.status_code == 404
    assert response.json()["detail"] == "Brief not found"


def test_update_brief():

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


def test_update_missing_brief():

    response = client.put(
        "/briefs/999",
        json={
            "title": "Updated Website",
            "description": "Updated description"
        }
    )


    assert response.status_code == 404
    assert response.json()["detail"] == "Brief not found"


def test_delete_brief():

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


def test_delete_missing_brief():

    response = client.delete("/briefs/999")


    assert response.status_code == 404
    assert response.json()["detail"] == "Brief not found"


def test_create_brief_with_empty_title():
    response = client.post(
        "/briefs",
        json={
            "title": "",
            "description": "Build a website"
        }
    )


    assert response.status_code == 422


def test_create_brief_with_whitespace_title():
    response = client.post(
        "/briefs",
        json={
            "title": "   ",
            "description": "Build a website"
        }
    )


    assert response.status_code == 422


def test_create_brief_with_long_title():
    response = client.post(
        "/briefs",
        json={
            "title": "A" * 101,
            "description": "Build a website"
        }
    )

    assert response.status_code == 422


def test_create_brief_with_long_description():
    response = client.post(
        "/briefs",
        json={
            "title": "AgencyOS",
            "description": "A" * 1001
        }
    )


    assert response.status_code == 422


def test_create_brief_trims_whitespace():
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


def test_create_brief_rejects_integer_title():
    response = client.post(
        "/briefs",
        json={
            "title": 12345,
            "description": "Build a website"
        }
    )


    assert response.status_code == 422

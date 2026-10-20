from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_wrong_password():
    response = client.post(
        "/auth/login",
        json={
            "email": "anshika@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401


def test_unauthorized_me():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_train_search():
    response = client.get(
        "/trains/search",
        params={
            "source": "NDLS",
            "destination": "CNB",
            "journey_date": "2026-10-21",
        },
    )

    assert response.status_code == 200

    trains = response.json()

    assert len(trains) >= 1
    assert trains[0]["train_number"] == "12001"
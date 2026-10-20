from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from app.auth.security import hash_password
from app.database import get_session
from app.main import app
from app.models import PasswordResetToken, User


@pytest.fixture
def auth_client(tmp_path):
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'auth-tests.db'}",
        connect_args={"check_same_thread": False, "timeout": 30},
    )
    SQLModel.metadata.create_all(test_engine)

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with Session(test_engine) as session:
        user = User(
            name="Test Passenger",
            email="reset-passenger@example.com",
            password_hash=hash_password("OldRandomPass123"),
        )
        session.add(user)
        session.commit()

    with TestClient(app) as client:
        yield client, test_engine

    app.dependency_overrides.pop(get_session, None)
    test_engine.dispose()


def test_password_reset_token_works_once_and_changes_password(auth_client):
    client, test_engine = auth_client
    forgot = client.post(
        "/auth/forgot-password",
        params={"email": "reset-passenger@example.com"},
    )
    assert forgot.status_code == 200
    token = forgot.json()["reset_token"]

    reset = client.post(
        "/auth/reset-password",
        params={"token": token, "new_password": "NewRandomPass123"},
    )
    assert reset.status_code == 200

    replay = client.post(
        "/auth/reset-password",
        params={"token": token, "new_password": "AnotherRandomPass123"},
    )
    assert replay.status_code == 400

    login = client.post(
        "/auth/login",
        json={
            "email": "reset-passenger@example.com",
            "password": "NewRandomPass123",
        },
    )
    assert login.status_code == 200

    with Session(test_engine) as session:
        record = session.exec(select(PasswordResetToken)).one()
        assert record.used is True


def test_expired_password_reset_token_is_rejected(auth_client):
    client, test_engine = auth_client
    forgot = client.post(
        "/auth/forgot-password",
        params={"email": "reset-passenger@example.com"},
    )
    assert forgot.status_code == 200
    token = forgot.json()["reset_token"]

    with Session(test_engine) as session:
        record = session.exec(
            select(PasswordResetToken).where(PasswordResetToken.token == token)
        ).one()
        record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        session.add(record)
        session.commit()

    reset = client.post(
        "/auth/reset-password",
        params={"token": token, "new_password": "NewRandomPass123"},
    )
    assert reset.status_code == 400
    assert reset.json()["detail"] == "Reset token expired"

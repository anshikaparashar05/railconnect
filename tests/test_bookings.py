from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from app.auth.security import create_access_token
from app.database import get_session
from app.main import app
from app.models import Booking, Train, User


@pytest.fixture
def booking_client(tmp_path):
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'booking-tests.db'}",
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
            email="passenger@example.com",
            password_hash="unused-in-this-test",
        )
        train = Train(
            train_number="TEST001",
            train_name="Test Express",
            source_station_id=1,
            destination_station_id=2,
            departure_time="09:00",
            arrival_time="12:00",
            journey_date="2030-01-01",
            fare=100,
            total_seats=1,
            available_seats=1,
        )
        session.add(user)
        session.add(train)
        session.commit()
        session.refresh(user)
        user_id = user.id
        train_id = train.id

    token = create_access_token(user_id)
    with TestClient(app) as client:
        yield client, test_engine, train_id, {"Authorization": f"Bearer {token}"}

    app.dependency_overrides.pop(get_session, None)
    test_engine.dispose()


def test_concurrent_bookings_cannot_claim_the_same_last_seat(booking_client):
    client, test_engine, train_id, headers = booking_client

    def request_booking(_):
        return client.post(
            "/bookings/",
            params={"train_id": train_id, "passenger_name": "Test Passenger"},
            headers=headers,
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        responses = list(pool.map(request_booking, range(8)))

    assert sum(response.status_code == 200 for response in responses) == 1
    assert sum(response.status_code == 400 for response in responses) == 7

    with Session(test_engine) as session:
        train = session.get(Train, train_id)
        bookings = session.exec(select(Booking)).all()
        assert train.available_seats == 0
        assert len(bookings) == 1
        assert bookings[0].seat_number == 1


def test_concurrent_cancellations_release_a_seat_only_once(booking_client):
    client, test_engine, train_id, headers = booking_client
    response = client.post(
        "/bookings/",
        params={"train_id": train_id, "passenger_name": "Test Passenger"},
        headers=headers,
    )
    assert response.status_code == 200
    pnr = response.json()["pnr"]

    def request_cancellation(_):
        return client.delete(f"/bookings/{pnr}", headers=headers)

    with ThreadPoolExecutor(max_workers=8) as pool:
        responses = list(pool.map(request_cancellation, range(8)))

    assert sum(response.status_code == 200 for response in responses) == 1
    assert sum(response.status_code == 400 for response in responses) == 7

    with Session(test_engine) as session:
        train = session.get(Train, train_id)
        booking = session.exec(select(Booking)).one()
        assert train.available_seats == 1
        assert booking.status == "cancelled"

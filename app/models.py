from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    email: str = Field(index=True, unique=True)
    password_hash: str

    role: str = "passenger"
    is_active: bool = True

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Station(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    code: str = Field(index=True, unique=True)

    city: str
    state: str

    is_active: bool = True


class Train(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    train_number: str = Field(index=True, unique=True)
    train_name: str

    source_station_id: int
    destination_station_id: int

    departure_time: str
    arrival_time: str
    journey_date: str

    fare: float
    total_seats: int
    available_seats: int

    is_active: bool = True


class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    pnr: str = Field(index=True, unique=True)

    user_id: int
    train_id: int

    passenger_name: str
    seat_number: int

    fare: float
    status: str = "confirmed"

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class PasswordResetToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    token: str = Field(index=True, unique=True)
    user_id: int

    expires_at: datetime
    used: bool = False
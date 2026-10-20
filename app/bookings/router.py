import random
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.database import get_session
from app.models import Booking, Train, User

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


def generate_pnr():
    return "RC" + "".join(
        random.choices(string.digits, k=8)
    )


@router.post("/")
def create_booking(
    train_id: int,
    passenger_name: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Claim a seat with one conditional write. Competing updates are serialized
    # by the database, so only a request that sees availability can claim a seat.
    train = session.exec(
        update(Train)
        .where(
            Train.id == train_id,
            Train.is_active.is_(True),
            Train.available_seats > 0,
        )
        .values(available_seats=Train.available_seats - 1)
        .returning(Train.total_seats, Train.available_seats, Train.fare)
    ).first()

    if train is None:
        current_train = session.get(Train, train_id)
        if current_train is None:
            raise HTTPException(status_code=404, detail="Train not found")
        if not current_train.is_active:
            raise HTTPException(status_code=400, detail="Train is inactive")
        raise HTTPException(status_code=400, detail="All seats are booked")

    seat_number = train.total_seats - train.available_seats
    pnr = generate_pnr()
    while session.exec(
        select(Booking).where(Booking.pnr == pnr)
    ).first():
        pnr = generate_pnr()

    booking = Booking(
        pnr=pnr,
        user_id=current_user.id,
        train_id=train_id,
        passenger_name=passenger_name,
        seat_number=seat_number,
        fare=train.fare,
        status="confirmed",
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


@router.get("/")
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    bookings = session.exec(
        select(Booking).where(Booking.user_id == current_user.id)
    ).all()
    return bookings


@router.get("/{pnr}")
def get_booking(
    pnr: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    booking = session.exec(
        select(Booking).where(
            Booking.pnr == pnr,
            Booking.user_id == current_user.id
        )
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.delete("/{pnr}")
def cancel_booking(
    pnr: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    cancelled = session.exec(
        update(Booking)
        .where(
            Booking.pnr == pnr,
            Booking.user_id == current_user.id,
            Booking.status == "confirmed",
        )
        .values(status="cancelled")
        .returning(Booking.train_id, Booking.seat_number)
    ).first()

    if cancelled is None:
        booking = session.exec(
            select(Booking).where(
                Booking.pnr == pnr,
                Booking.user_id == current_user.id,
            )
        ).first()
        if booking is None:
            raise HTTPException(status_code=404, detail="Booking not found")
        raise HTTPException(status_code=400, detail="Booking already cancelled")

    restored = session.exec(
        update(Train)
        .where(
            Train.id == cancelled.train_id,
            Train.available_seats < Train.total_seats,
        )
        .values(available_seats=Train.available_seats + 1)
        .returning(Train.id)
    ).first()

    if restored is None:
        session.rollback()
        raise HTTPException(status_code=409, detail="Unable to restore the seat")

    session.commit()
    return {
        "message": "Booking cancelled successfully",
        "pnr": pnr,
        "seat_number": cancelled.seat_number,
    }

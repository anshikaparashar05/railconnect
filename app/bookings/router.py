import random
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Booking, Train, User
from app.auth.dependencies import get_current_user

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
    train = session.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=404,
            detail="Train not found"
        )

    if not train.is_active:
        raise HTTPException(
            status_code=400,
            detail="Train is inactive"
        )

    if train.available_seats <= 0:
        raise HTTPException(
            status_code=400,
            detail="All seats are booked"
        )

    # Assign next seat number
    seat_number = train.total_seats - train.available_seats + 1

    # Reduce available seats
    train.available_seats -= 1

    pnr = generate_pnr()

    # Make sure PNR is unique
    while session.exec(
        select(Booking).where(Booking.pnr == pnr)
    ).first():
        pnr = generate_pnr()

    booking = Booking(
        pnr=pnr,
        user_id=current_user.id,
        train_id=train.id,
        passenger_name=passenger_name,
        seat_number=seat_number,
        fare=train.fare,
        status="confirmed",
    )

    session.add(booking)
    session.add(train)
    session.commit()
    session.refresh(booking)

    return booking


@router.get("/")
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    bookings = session.exec(
        select(Booking).where(
            Booking.user_id == current_user.id
        )
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
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return booking


@router.delete("/{pnr}")
def cancel_booking(
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
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Booking already cancelled"
        )

    train = session.get(Train, booking.train_id)

    if train:
        train.available_seats += 1
        session.add(train)

    booking.status = "cancelled"

    session.add(booking)
    session.commit()

    return {
        "message": "Booking cancelled successfully",
        "pnr": booking.pnr,
        "seat_number": booking.seat_number,
    }
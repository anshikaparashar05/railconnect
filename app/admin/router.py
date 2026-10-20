from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Station, Train
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# ---------------- STATIONS ----------------

@router.post("/stations", status_code=status.HTTP_201_CREATED)
def create_station(
    station_data: Station,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    existing_station = session.exec(
        select(Station).where(Station.code == station_data.code)
    ).first()

    if existing_station:
        raise HTTPException(
            status_code=400,
            detail="Station code already exists"
        )

    session.add(station_data)
    session.commit()
    session.refresh(station_data)

    return station_data


@router.get("/stations")
def get_stations(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return session.exec(select(Station)).all()


# ---------------- TRAINS ----------------

@router.post("/trains", status_code=status.HTTP_201_CREATED)
def create_train(
    train_data: Train,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    existing_train = session.exec(
        select(Train).where(
            Train.train_number == train_data.train_number
        )
    ).first()

    if existing_train:
        raise HTTPException(
            status_code=400,
            detail="Train number already exists"
        )

    if train_data.total_seats <= 0:
        raise HTTPException(
            status_code=400,
            detail="Total seats must be greater than zero"
        )

    train_data.available_seats = train_data.total_seats

    session.add(train_data)
    session.commit()
    session.refresh(train_data)

    return train_data


@router.get("/trains")
def get_trains(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return session.exec(select(Train)).all()
@router.put("/trains/{train_id}")
def update_train(
    train_id: int,
    train_data: Train,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    train = session.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=404,
            detail="Train not found"
        )

    train.train_number = train_data.train_number
    train.train_name = train_data.train_name
    train.source_station_id = train_data.source_station_id
    train.destination_station_id = train_data.destination_station_id
    train.departure_time = train_data.departure_time
    train.arrival_time = train_data.arrival_time
    train.journey_date = train_data.journey_date
    train.fare = train_data.fare
    train.total_seats = train_data.total_seats
    train.available_seats = train_data.available_seats
    train.is_active = train_data.is_active

    session.add(train)
    session.commit()
    session.refresh(train)

    return train


@router.patch("/trains/{train_id}/deactivate")
def deactivate_train(
    train_id: int,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    train = session.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=404,
            detail="Train not found"
        )

    train.is_active = False

    session.add(train)
    session.commit()
    session.refresh(train)

    return {
        "message": "Train deactivated successfully",
        "train_id": train.id
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Train, Station
from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/trains",
    tags=["Trains"]
)


@router.get("/search")
def search_trains(
    source: str,
    destination: str,
    journey_date: str,
    session: Session = Depends(get_session),
):
    source_station = session.exec(
        select(Station).where(Station.code == source.upper())
    ).first()

    destination_station = session.exec(
        select(Station).where(Station.code == destination.upper())
    ).first()

    if not source_station:
        raise HTTPException(
            status_code=404,
            detail="Source station not found"
        )

    if not destination_station:
        raise HTTPException(
            status_code=404,
            detail="Destination station not found"
        )

    trains = session.exec(
        select(Train).where(
            Train.source_station_id == source_station.id,
            Train.destination_station_id == destination_station.id,
            Train.journey_date == journey_date,
            Train.is_active == True,
        )
    ).all()

    return trains
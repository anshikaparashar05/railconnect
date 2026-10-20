from fastapi import FastAPI


from app.bookings.router import router as booking_router
from app.trains.router import router as train_router
from app.database import create_db_and_tables
from app.auth.router import router as auth_router
from app.admin.router import router as admin_router


app = FastAPI(
    title="RailConnect API",
    description="Mini Railway Booking Backend",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(train_router)
app.include_router(booking_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to RailConnect API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
# RailConnect 🚆

A mini railway ticket booking backend built using FastAPI, Python and SQLite.

## 📌 Project Overview

RailConnect is a backend system for a fictional railway booking platform.

It provides APIs for:

- Passenger registration and login
- JWT authentication
- Password hashing using bcrypt
- Password reset
- Passenger profile
- Admin station management
- Admin train management
- Train search
- Seat availability
- Ticket booking
- Unique PNR generation
- Booking history
- Ticket cancellation
- Seat restoration after cancellation
- Protected APIs
- API testing using pytest

## 🛠️ Technology Stack

- Python
- FastAPI
- SQLModel
- SQLite
- Pydantic
- Pydantic Settings
- JWT
- python-jose
- bcrypt
- Uvicorn
- pytest
- HTTPX
- Swagger UI

## 📁 Project Structure

```text
railconnect/
├── app/
│   ├── auth/
│   │   ├── router.py
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── admin/
│   │   └── router.py
│   ├── trains/
│   │   └── router.py
│   ├── bookings/
│   │   └── router.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── config.py
│   └── main.py
├── tests/
│   └── test_api.py
├── screenshots/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

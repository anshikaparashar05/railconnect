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

```

## 📸 API Screenshots

The following screenshots show the main RailConnect API workflows in Swagger UI:

### Authentication

| Registration | Login | Unauthorized request (401) |
|---|---|---|
| ![Passenger registration](screenshots/01-register.png) | ![Successful login](screenshots/02-login.png) | ![Unauthorized request (401) response](screenshots/03-unauthorized.png) |

### Admin and train search

| Create station | Create train | Search trains |
|---|---|---|
| ![Admin creates a station](screenshots/04-admin-station.png) | ![Admin creates a train](screenshots/05-admin-train.png) | ![Train search response](screenshots/06-train-search.png) |

### Booking and cancellation

| Submit booking | Booking confirmation with PNR | Cancel booking |
|---|---|---|
| ![Booking request](screenshots/07.1-booking-pnr.png) | ![Booking response with PNR](screenshots/07.2-booking-pnr.png) | ![Booking cancellation response](screenshots/08-cancellation.png) |

### Tests

![Pytest results: 4 passed](screenshots/09-tests.png)

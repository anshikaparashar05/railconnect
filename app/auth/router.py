from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import User, PasswordResetToken
from app.schemas import UserRegister, UserResponse, UserLogin, TokenResponse
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ---------------- REGISTER ----------------

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserRegister,
    session: Session = Depends(get_session)
):
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


# ---------------- LOGIN ----------------

@router.post("/login", response_model=TokenResponse)
def login(
    user_data: UserLogin,
    session: Session = Depends(get_session)
):
    user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ---------------- CURRENT USER ----------------

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


# ---------------- FORGOT PASSWORD ----------------

@router.post("/forgot-password")
def forgot_password(
    email: str,
    session: Session = Depends(get_session),
):
    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    token = secrets.token_urlsafe(32)

    reset_token = PasswordResetToken(
        token=token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    )

    session.add(reset_token)
    session.commit()

    return {
        "message": "Password reset token generated",
        "reset_token": token
    }


# ---------------- RESET PASSWORD ----------------

@router.post("/reset-password")
def reset_password(
    token: str,
    new_password: str,
    session: Session = Depends(get_session),
):
    reset_token = session.exec(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token
        )
    ).first()

    if not reset_token:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset token"
        )

    if reset_token.used:
        raise HTTPException(
            status_code=400,
            detail="Reset token already used"
        )

    expires_at = reset_token.expires_at
    if expires_at.tzinfo is None:
        # SQLite may return stored datetimes without timezone information.
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Reset token expired"
        )

    user = session.get(User, reset_token.user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.password_hash = hash_password(new_password)
    reset_token.used = True

    session.add(user)
    session.add(reset_token)
    session.commit()

    return {
        "message": "Password reset successfully"
    }
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {
        "message": "Logout successful. Please remove the access token from the client."
    }
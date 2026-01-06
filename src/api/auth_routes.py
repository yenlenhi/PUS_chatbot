"""
Authentication routes for JWT token generation
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Form
from pydantic import BaseModel

from config.settings import (
    LOCKOUT_MINUTES,
    MAX_FAILED_LOGIN_ATTEMPTS,
    USE_FAKE_USERS,
)
from src.auth.jwt_handler import create_token_for_user
from src.auth.security import verify_password
from src.services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["authentication"])


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    """Login request model"""

    username: str
    password: str


class UserCreate(BaseModel):
    """User creation model"""

    username: str
    password: str
    full_name: Optional[str] = None


FAKE_USERS_DB = {}
FAKE_LOGIN_STATE = {}

if USE_FAKE_USERS:
    # Fake user database for local development
    # Pre-hashed passwords to avoid bcrypt version conflicts
    # admin123: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXc3rKHzC
    # user123: $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW
    FAKE_USERS_DB = {
        "admin": {
            "username": "admin",
            "full_name": "System Administrator",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXc3rKHzC",
            "disabled": False,
            "scopes": ["admin", "user"],
        },
        "user": {
            "username": "user",
            "full_name": "Regular User",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "disabled": False,
            "scopes": ["user"],
        },
    }


def _fake_authenticate_user(username: str, password: str):
    user = FAKE_USERS_DB.get(username)
    if not user:
        return None, "invalid_credentials"

    state = FAKE_LOGIN_STATE.get(username, {"failed_attempts": 0, "lockout_until": None})
    lockout_until = state.get("lockout_until")
    now = datetime.now(timezone.utc)
    if lockout_until and lockout_until > now:
        return None, "locked"

    if verify_password(password, user["hashed_password"]):
        FAKE_LOGIN_STATE[username] = {"failed_attempts": 0, "lockout_until": None}
        return user, None

    failed_attempts = state.get("failed_attempts", 0) + 1
    lockout_value = None
    error = "invalid_credentials"
    if failed_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
        lockout_value = now + timedelta(minutes=LOCKOUT_MINUTES)
        error = "locked"
    FAKE_LOGIN_STATE[username] = {
        "failed_attempts": failed_attempts,
        "lockout_until": lockout_value,
    }
    return None, error


def authenticate_user(username: str, password: str):
    """Authenticate a user"""
    if USE_FAKE_USERS:
        return _fake_authenticate_user(username, password)

    auth_service = AuthService()
    result = auth_service.authenticate_user(username, password)
    return result.user, result.error


def _raise_auth_error(error: Optional[str]):
    if not error:
        return
    if error == "locked":
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is locked due to too many failed login attempts.",
        )
    if error == "disabled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled.",
        )
    if error == "server_error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error.",
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@auth_router.post("/token", response_model=Token)
async def login(username: str = Form(...), password: str = Form(...)):
    """
    OAuth2 compatible token login endpoint
    Use this endpoint to get an access token
    """
    user, error = authenticate_user(username, password)
    _raise_auth_error(error)

    access_token = create_token_for_user(
        username=user["username"],
        user_id=user["username"],
        scopes=user.get("scopes", []),
    )

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/login", response_model=Token)
async def login_json(login_data: LoginRequest):
    """
    JSON login endpoint (alternative to OAuth2 form)
    """
    user, error = authenticate_user(login_data.username, login_data.password)
    _raise_auth_error(error)

    access_token = create_token_for_user(
        username=user["username"],
        user_id=user["username"],
        scopes=user.get("scopes", []),
    )

    return {"access_token": access_token, "token_type": "bearer"}

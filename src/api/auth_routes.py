"""
Authentication routes for JWT token generation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from src.auth.jwt_handler import create_token_for_user
from src.auth.security import verify_password

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


# Fake user database for demonstration
# In production, replace with real database
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


def authenticate_user(username: str, password: str):
    """Authenticate a user"""
    user = FAKE_USERS_DB.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


@auth_router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login endpoint
    Use this endpoint to get an access token
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_token_for_user(
        username=user["username"],
        user_id=user["username"],
        scopes=user.get("scopes", []),
    )

    return {"access_token": access_token, "token_type": "bearer"}

"""
Authentication routes for JWT token generation
Now uses PostgreSQL database for user management
"""

from fastapi import APIRouter, HTTPException, status, Form, Depends
from pydantic import BaseModel
from src.auth.jwt_handler import create_token_for_user
from src.services.user_service import get_user_service, UserService
from src.utils.logger import log

auth_router = APIRouter(prefix="/auth", tags=["authentication"])


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    """Login request model"""

    username: str
    password: str


@auth_router.post("/token", response_model=Token)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    user_service: UserService = Depends(get_user_service),
):
    """
    OAuth2 compatible token login endpoint
    Use this endpoint to get an access token

    For testing in Swagger UI, use:
    - Username: admin or user
    - Password: Admin123 or User123
    """
    # Authenticate user from database
    user = user_service.authenticate_user(username, password)

    if not user:
        log.warning(f"Failed login attempt for username: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    log.info(f"User logged in: {user.username}")

    access_token = create_token_for_user(
        username=user.username,
        user_id=str(user.id),
        scopes=user.roles,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/login", response_model=Token)
async def login_json(
    login_data: LoginRequest, user_service: UserService = Depends(get_user_service)
):
    """
    JSON login endpoint (alternative to OAuth2 form)

    Request body:
    {
        "username": "admin",
        "password": "Admin123"
    }
    """
    # Authenticate user from database
    user = user_service.authenticate_user(login_data.username, login_data.password)

    if not user:
        log.warning(f"Failed login attempt for username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    log.info(f"User logged in: {user.username}")

    access_token = create_token_for_user(
        username=user.username,
        user_id=str(user.id),
        scopes=user.roles,
    )

    return {"access_token": access_token, "token_type": "bearer"}

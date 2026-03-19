"""
Async JWT Token Handler for authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
import uuid

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


class TokenData(BaseModel):
    """Token data model"""

    username: Optional[str] = None
    user_id: Optional[str] = None
    scopes: list[str] = []


class User(BaseModel):
    """User model"""

    username: str
    user_id: str
    disabled: Optional[bool] = None
    scopes: list[str] = []


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_token_for_user(username: str, user_id: str, scopes: list[str]) -> str:
    """
    Create JWT token for a specific user

    Args:
        username: User's username
        user_id: User's ID
        scopes: User's permission scopes

    Returns:
        JWT token string
    """
    token_data = {
        "sub": username,
        "user_id": user_id,
        "scopes": scopes,
    }
    return create_access_token(data=token_data)


def verify_access_token(token: str) -> TokenData:
    """
    Verify and decode JWT access token

    Args:
        token: JWT token string

    Returns:
        TokenData object

    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        scopes: list[str] = payload.get("scopes", [])

        if username is None or user_id is None:
            raise credentials_exception

        token_data = TokenData(username=username, user_id=user_id, scopes=scopes)
        return token_data

    except JWTError:
        raise credentials_exception


async def get_current_user_async(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Get current authenticated user from JWT token (async version)

    Args:
        token: JWT token from request

    Returns:
        User object if authenticated, None if no token provided

    Raises:
        HTTPException: If token is invalid or user is disabled
    """
    if not token:
        return None

    try:
        # Verify token
        token_data = verify_access_token(token)

        # Import here to avoid circular imports
        from src.services.async_user_service import get_async_user_service

        # Get user from database
        user_service = await get_async_user_service()
        user_in_db = await user_service.get_user_by_username(token_data.username)

        if not user_in_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user_in_db.disabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        return User(
            username=user_in_db.username,
            user_id=str(user_in_db.id),
            disabled=user_in_db.disabled,
            scopes=getattr(user_in_db, "scopes", user_in_db.roles),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin_async(
    current_user: Optional[User] = Depends(get_current_user_async),
) -> User:
    """
    Require an authenticated admin user.

    Returns:
        Authenticated user with admin scope

    Raises:
        HTTPException: If the request is unauthenticated or lacks admin scope
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


# Alias for compatibility
get_current_user = get_current_user_async


# Alias for compatibility
require_admin = require_admin_async

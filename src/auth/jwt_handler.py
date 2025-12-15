"""
JWT Token Handler for authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

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
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> TokenData:
    """
    Verify and decode a JWT access token

    Args:
        token: JWT token string

    Returns:
        TokenData object with decoded token information

    Raises:
        HTTPException: If token is invalid or expired
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
        scopes: list = payload.get("scopes", [])

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username, user_id=user_id, scopes=scopes)
        return token_data

    except JWTError:
        raise credentials_exception


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Get current authenticated user from JWT token

    Args:
        token: JWT token from request

    Returns:
        User object if authenticated, None if no token provided

    Raises:
        HTTPException: If token is invalid
    """
    if token is None:
        return None

    token_data = verify_access_token(token)

    # In production, fetch user from database
    # For now, return user from token data
    user = User(
        username=token_data.username,
        user_id=token_data.user_id or token_data.username,
        scopes=token_data.scopes,
    )

    return user


def create_token_for_user(username: str, user_id: str, scopes: list[str] = None) -> str:
    """
    Create an access token for a user

    Args:
        username: Username
        user_id: User ID
        scopes: List of permission scopes

    Returns:
        JWT token string
    """
    if scopes is None:
        scopes = []

    token_data = {"sub": username, "user_id": user_id, "scopes": scopes}

    return create_access_token(token_data)

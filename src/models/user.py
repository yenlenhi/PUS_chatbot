"""
User models and schemas for authentication and authorization
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator
import re


class UserRole(BaseModel):
    """User role model"""

    role: str = Field(..., description="Role name (admin, user, etc)")


class UserBase(BaseModel):
    """Base user model"""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username"
    )
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(
        None, max_length=100, description="User's full name"
    )
    disabled: bool = Field(default=False, description="Whether user is disabled")


class UserCreate(UserBase):
    """Model for creating a new user"""

    password: str = Field(
        ..., min_length=8, description="User password (min 8 characters)"
    )
    roles: List[str] = Field(default=["user"], description="User roles")

    @validator("password")
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for at least one uppercase, one lowercase, and one digit
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        return v

    @validator("roles")
    def validate_roles(cls, v):
        """Validate roles"""
        valid_roles = {
            "admin",
            "user",
            "moderator",
            "documents:read",
            "documents:write",
        }
        for role in v:
            if role not in valid_roles:
                raise ValueError(f"Invalid role: {role}. Valid roles: {valid_roles}")
        return v


class UserUpdate(BaseModel):
    """Model for updating user information"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    disabled: Optional[bool] = None
    roles: Optional[List[str]] = None

    @validator("roles")
    def validate_roles(cls, v):
        """Validate roles"""
        if v is None:
            return v
        valid_roles = {
            "admin",
            "user",
            "moderator",
            "documents:read",
            "documents:write",
        }
        for role in v:
            if role not in valid_roles:
                raise ValueError(f"Invalid role: {role}. Valid roles: {valid_roles}")
        return v


class UserChangePassword(BaseModel):
    """Model for changing password"""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @validator("new_password")
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        return v


class UserResponse(UserBase):
    """User response model (without password)"""

    id: int = Field(..., description="User ID")
    roles: List[str] = Field(default=[], description="User roles")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """User model as stored in database"""

    hashed_password: str = Field(..., description="Hashed password")


class UserListResponse(BaseModel):
    """Response model for user list"""

    total: int = Field(..., description="Total number of users")
    users: List[UserResponse] = Field(..., description="List of users")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=20, description="Items per page")

"""
Authentication module for University Chatbot
"""

from .jwt_handler import (
    create_access_token,
    verify_access_token,
    get_current_user,
    require_admin,
)
from .security import (
    verify_password,
    get_password_hash,
    oauth2_scheme,
)

__all__ = [
    "create_access_token",
    "verify_access_token",
    "get_current_user",
    "require_admin",
    "verify_password",
    "get_password_hash",
    "oauth2_scheme",
]

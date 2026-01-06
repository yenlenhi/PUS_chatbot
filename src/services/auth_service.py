"""
Authentication service for validating users against the database.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import text

from config.settings import (
    LOCKOUT_MINUTES as DEFAULT_LOCKOUT_MINUTES,
    MAX_FAILED_LOGIN_ATTEMPTS as DEFAULT_MAX_FAILED_LOGIN_ATTEMPTS,
)
from src.auth.security import verify_password
from src.services.postgres_database_service import PostgresDatabaseService
from src.utils.logger import log


@dataclass
class AuthResult:
    """Authentication result details."""

    user: Optional[dict]
    error: Optional[str] = None
    lockout_until: Optional[datetime] = None


class AuthService:
    """Service handling authentication and lockout policy."""

    def __init__(
        self,
        db_service: Optional[PostgresDatabaseService] = None,
        max_failed_attempts: int = DEFAULT_MAX_FAILED_LOGIN_ATTEMPTS,
        lockout_minutes: int = DEFAULT_LOCKOUT_MINUTES,
    ):
        self.db_service = db_service or PostgresDatabaseService()
        self.max_failed_attempts = max_failed_attempts
        self.lockout_minutes = lockout_minutes

    def authenticate_user(self, username: str, password: str) -> AuthResult:
        """Authenticate a user against the database with lockout policy."""
        session = self.db_service.SessionLocal()
        try:
            row = session.execute(
                text(
                    """
                    SELECT username, full_name, hashed_password, disabled, scopes,
                           failed_login_attempts, lockout_until
                    FROM users
                    WHERE username = :username
                    """
                ),
                {"username": username},
            ).mappings().first()
            if not row:
                return AuthResult(user=None, error="invalid_credentials")

            if row["disabled"]:
                return AuthResult(user=None, error="disabled")

            lockout_until = row["lockout_until"]
            now = datetime.now(timezone.utc)
            if lockout_until and lockout_until.replace(tzinfo=timezone.utc) > now:
                return AuthResult(
                    user=None, error="locked", lockout_until=lockout_until
                )

            if verify_password(password, row["hashed_password"]):
                session.execute(
                    text(
                        """
                        UPDATE users
                        SET failed_login_attempts = 0,
                            lockout_until = NULL,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE username = :username
                        """
                    ),
                    {"username": username},
                )
                session.commit()
                user = {
                    "username": row["username"],
                    "full_name": row["full_name"],
                    "disabled": row["disabled"],
                    "scopes": row["scopes"] or [],
                }
                return AuthResult(user=user)

            failed_attempts = (row["failed_login_attempts"] or 0) + 1
            lockout_until_value = None
            error = "invalid_credentials"
            if failed_attempts >= self.max_failed_attempts:
                lockout_until_value = now + timedelta(minutes=self.lockout_minutes)
                error = "locked"
            session.execute(
                text(
                    """
                    UPDATE users
                    SET failed_login_attempts = :failed_login_attempts,
                        lockout_until = :lockout_until,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE username = :username
                    """
                ),
                {
                    "failed_login_attempts": failed_attempts,
                    "lockout_until": lockout_until_value,
                    "username": username,
                },
            )
            session.commit()
            return AuthResult(
                user=None,
                error=error,
                lockout_until=lockout_until_value,
            )
        except Exception:
            session.rollback()
            log.exception("Failed to authenticate user")
            return AuthResult(user=None, error="server_error")
        finally:
            session.close()

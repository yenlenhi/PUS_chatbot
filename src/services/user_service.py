"""
User Service for managing users in PostgreSQL database
"""

from typing import Optional, List
from sqlalchemy import text
from src.services.postgres_database_service import PostgresDatabaseService
from src.auth.security import get_password_hash, verify_password
from src.models.user import UserCreate, UserUpdate, UserResponse, UserInDB
from src.utils.logger import log


class UserService:
    """Service for user management operations"""

    def __init__(self):
        """Initialize user service"""
        self.db = PostgresDatabaseService()
        log.info("UserService initialized")

    def create_tables(self):
        """Create users and user_roles tables if they don't exist"""
        try:
            with self.db.engine.connect() as conn:
                # Create users table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL,
                        full_name VARCHAR(100),
                        disabled BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """
                    )
                )

                # Create user_roles table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS user_roles (
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        role VARCHAR(50) NOT NULL,
                        PRIMARY KEY (user_id, role)
                    )
                """
                    )
                )

                # Create indexes
                conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
                """
                    )
                )
                conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
                """
                    )
                )

                conn.commit()
                log.info("User tables created successfully")

        except Exception as e:
            log.error(f"Error creating user tables: {e}")
            raise

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Create a new user

        Args:
            user_data: User creation data

        Returns:
            Created user response

        Raises:
            ValueError: If username or email already exists
        """
        try:
            with self.db.engine.connect() as conn:
                # Check if username exists
                result = conn.execute(
                    text("SELECT id FROM users WHERE username = :username"),
                    {"username": user_data.username},
                ).fetchone()

                if result:
                    raise ValueError(f"Username '{user_data.username}' already exists")

                # Check if email exists
                result = conn.execute(
                    text("SELECT id FROM users WHERE email = :email"),
                    {"email": user_data.email},
                ).fetchone()

                if result:
                    raise ValueError(f"Email '{user_data.email}' already exists")

                # Hash password
                hashed_password = get_password_hash(user_data.password)

                # Insert user
                result = conn.execute(
                    text(
                        """
                        INSERT INTO users (username, email, hashed_password, full_name, disabled)
                        VALUES (:username, :email, :hashed_password, :full_name, :disabled)
                        RETURNING id, username, email, full_name, disabled, created_at, updated_at
                    """
                    ),
                    {
                        "username": user_data.username,
                        "email": user_data.email,
                        "hashed_password": hashed_password,
                        "full_name": user_data.full_name,
                        "disabled": user_data.disabled,
                    },
                )

                user_row = result.fetchone()
                user_id = user_row[0]

                # Insert roles
                for role in user_data.roles:
                    conn.execute(
                        text(
                            "INSERT INTO user_roles (user_id, role) VALUES (:user_id, :role)"
                        ),
                        {"user_id": user_id, "role": role},
                    )

                conn.commit()

                # Fetch created user with roles
                created_user = self.get_user_by_id(user_id)
                log.info(f"User created: {user_data.username} (ID: {user_id})")

                return created_user

        except ValueError as e:
            raise e
        except Exception as e:
            log.error(f"Error creating user: {e}")
            raise

    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                        SELECT id, username, email, full_name, disabled, created_at, updated_at
                        FROM users
                        WHERE id = :user_id
                    """
                    ),
                    {"user_id": user_id},
                ).fetchone()

                if not result:
                    return None

                # Get user roles
                roles_result = conn.execute(
                    text("SELECT role FROM user_roles WHERE user_id = :user_id"),
                    {"user_id": user_id},
                ).fetchall()

                roles = [row[0] for row in roles_result]

                return UserResponse(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    full_name=result[3],
                    disabled=result[4],
                    created_at=result[5],
                    updated_at=result[6],
                    roles=roles,
                )

        except Exception as e:
            log.error(f"Error getting user by ID: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get user by username (includes hashed password for authentication)"""
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                        SELECT id, username, email, hashed_password, full_name, 
                               disabled, created_at, updated_at
                        FROM users
                        WHERE username = :username
                    """
                    ),
                    {"username": username},
                ).fetchone()

                if not result:
                    return None

                # Get user roles
                roles_result = conn.execute(
                    text("SELECT role FROM user_roles WHERE user_id = :user_id"),
                    {"user_id": result[0]},
                ).fetchall()

                roles = [row[0] for row in roles_result]

                return UserInDB(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    hashed_password=result[3],
                    full_name=result[4],
                    disabled=result[5],
                    created_at=result[6],
                    updated_at=result[7],
                    roles=roles,
                )

        except Exception as e:
            log.error(f"Error getting user by username: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email"""
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                        SELECT id, username, email, full_name, disabled, created_at, updated_at
                        FROM users
                        WHERE email = :email
                    """
                    ),
                    {"email": email},
                ).fetchone()

                if not result:
                    return None

                # Get user roles
                roles_result = conn.execute(
                    text("SELECT role FROM user_roles WHERE user_id = :user_id"),
                    {"user_id": result[0]},
                ).fetchall()

                roles = [row[0] for row in roles_result]

                return UserResponse(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    full_name=result[3],
                    disabled=result[4],
                    created_at=result[5],
                    updated_at=result[6],
                    roles=roles,
                )

        except Exception as e:
            log.error(f"Error getting user by email: {e}")
            return None

    def list_users(
        self, skip: int = 0, limit: int = 20, disabled: Optional[bool] = None
    ) -> tuple[List[UserResponse], int]:
        """
        List users with pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            disabled: Filter by disabled status (None = all users)

        Returns:
            Tuple of (list of users, total count)
        """
        try:
            with self.db.engine.connect() as conn:
                # Build query
                where_clause = ""
                params = {"skip": skip, "limit": limit}

                if disabled is not None:
                    where_clause = "WHERE disabled = :disabled"
                    params["disabled"] = disabled

                # Get total count
                count_result = conn.execute(
                    text(f"SELECT COUNT(*) FROM users {where_clause}"), params
                ).fetchone()
                total = count_result[0]

                # Get users
                result = conn.execute(
                    text(
                        f"""
                        SELECT id, username, email, full_name, disabled, created_at, updated_at
                        FROM users
                        {where_clause}
                        ORDER BY created_at DESC
                        LIMIT :limit OFFSET :skip
                    """
                    ),
                    params,
                ).fetchall()

                users = []
                for row in result:
                    # Get roles for each user
                    roles_result = conn.execute(
                        text("SELECT role FROM user_roles WHERE user_id = :user_id"),
                        {"user_id": row[0]},
                    ).fetchall()

                    roles = [r[0] for r in roles_result]

                    users.append(
                        UserResponse(
                            id=row[0],
                            username=row[1],
                            email=row[2],
                            full_name=row[3],
                            disabled=row[4],
                            created_at=row[5],
                            updated_at=row[6],
                            roles=roles,
                        )
                    )

                return users, total

        except Exception as e:
            log.error(f"Error listing users: {e}")
            return [], 0

    def update_user(
        self, user_id: int, user_data: UserUpdate
    ) -> Optional[UserResponse]:
        """Update user information"""
        try:
            with self.db.engine.connect() as conn:
                # Check if user exists
                existing = conn.execute(
                    text("SELECT id FROM users WHERE id = :user_id"),
                    {"user_id": user_id},
                ).fetchone()

                if not existing:
                    return None

                # Build update query
                update_fields = []
                params = {"user_id": user_id}

                if user_data.email is not None:
                    update_fields.append("email = :email")
                    params["email"] = user_data.email

                if user_data.full_name is not None:
                    update_fields.append("full_name = :full_name")
                    params["full_name"] = user_data.full_name

                if user_data.disabled is not None:
                    update_fields.append("disabled = :disabled")
                    params["disabled"] = user_data.disabled

                if update_fields:
                    update_fields.append("updated_at = NOW()")
                    query = f"""
                        UPDATE users
                        SET {', '.join(update_fields)}
                        WHERE id = :user_id
                    """
                    conn.execute(text(query), params)

                # Update roles if provided
                if user_data.roles is not None:
                    # Delete existing roles
                    conn.execute(
                        text("DELETE FROM user_roles WHERE user_id = :user_id"),
                        {"user_id": user_id},
                    )

                    # Insert new roles
                    for role in user_data.roles:
                        conn.execute(
                            text(
                                "INSERT INTO user_roles (user_id, role) VALUES (:user_id, :role)"
                            ),
                            {"user_id": user_id, "role": role},
                        )

                conn.commit()

                log.info(f"User updated: ID {user_id}")
                return self.get_user_by_id(user_id)

        except Exception as e:
            log.error(f"Error updating user: {e}")
            raise

    def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        try:
            with self.db.engine.connect() as conn:
                # Get current hashed password
                result = conn.execute(
                    text("SELECT hashed_password FROM users WHERE id = :user_id"),
                    {"user_id": user_id},
                ).fetchone()

                if not result:
                    return False

                # Verify current password
                if not verify_password(current_password, result[0]):
                    raise ValueError("Current password is incorrect")

                # Hash new password
                new_hashed = get_password_hash(new_password)

                # Update password
                conn.execute(
                    text(
                        """
                        UPDATE users 
                        SET hashed_password = :hashed_password, updated_at = NOW()
                        WHERE id = :user_id
                    """
                    ),
                    {"hashed_password": new_hashed, "user_id": user_id},
                )

                conn.commit()
                log.info(f"Password changed for user ID: {user_id}")
                return True

        except ValueError as e:
            raise e
        except Exception as e:
            log.error(f"Error changing password: {e}")
            return False

    def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by setting disabled=True)"""
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                        UPDATE users 
                        SET disabled = TRUE, updated_at = NOW()
                        WHERE id = :user_id
                        RETURNING id
                    """
                    ),
                    {"user_id": user_id},
                ).fetchone()

                if not result:
                    return False

                conn.commit()
                log.info(f"User deleted (disabled): ID {user_id}")
                return True

        except Exception as e:
            log.error(f"Error deleting user: {e}")
            return False

    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate user with username and password

        Args:
            username: Username
            password: Plain text password

        Returns:
            UserInDB if authentication successful, None otherwise
        """
        user = self.get_user_by_username(username)

        if not user:
            return None

        if user.disabled:
            log.warning(f"Login attempt for disabled user: {username}")
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user


# Global instance
_user_service: Optional[UserService] = None


def get_user_service() -> UserService:
    """Get or create global UserService instance"""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service

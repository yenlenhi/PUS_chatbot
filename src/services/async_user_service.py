"""
Async User Service for managing users in PostgreSQL database
"""

from typing import Optional, List
from sqlalchemy import text
from src.services.async_postgres_database_service import get_async_database_service
from src.auth.security import get_password_hash, verify_password
from src.models.user import UserCreate, UserUpdate, UserResponse, UserInDB
from src.utils.logger import log


def text_no_prepare(sql: str):
    """Helper to create text() with prepare=False for pgbouncer compatibility"""
    return text(sql).execution_options(prepare=False)


class AsyncUserService:
    """Async service for user management operations"""

    def __init__(self):
        """Initialize async user service"""
        self.db_service = None
        log.info("AsyncUserService initialized")

    async def initialize(self):
        """Initialize database service"""
        if not self.db_service:
            self.db_service = await get_async_database_service()

    async def create_tables(self):
        """Create users and user_roles tables if they don't exist"""
        await self.initialize()

        try:
            async with self.db_service.engine.begin() as conn:
                # Create users table
                await conn.execute(
                    text_no_prepare(
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
                await conn.execute(
                    text_no_prepare(
                        """
                    CREATE TABLE IF NOT EXISTS user_roles (
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        role VARCHAR(50) NOT NULL,
                        PRIMARY KEY (user_id, role)
                    )
                """
                    )
                )

                # Create indexes - one by one for asyncpg compatibility
                await conn.execute(
                    text_no_prepare(
                        "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"
                    )
                )
                await conn.execute(
                    text_no_prepare(
                        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"
                    )
                )
                await conn.execute(
                    text_no_prepare(
                        "CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id)"
                    )
                )

                log.info("✅ User tables created successfully")

        except Exception as e:
            log.error(f"❌ Error creating user tables: {e}")
            raise

    async def create_user(self, user_data: UserCreate) -> UserInDB:
        """Create a new user"""
        await self.initialize()

        async with self.db_service.get_session() as session:
            try:
                # Check if username already exists
                result = await session.execute(
                    text_no_prepare("SELECT id FROM users WHERE username = :username"),
                    {"username": user_data.username},
                )
                if result.fetchone():
                    raise ValueError(f"Username '{user_data.username}' already exists")

                # Check if email already exists
                result = await session.execute(
                    text_no_prepare("SELECT id FROM users WHERE email = :email"),
                    {"email": user_data.email},
                )
                if result.fetchone():
                    raise ValueError(f"Email '{user_data.email}' already exists")

                # Hash password
                hashed_password = get_password_hash(user_data.password)

                # Insert user
                result = await session.execute(
                    text_no_prepare(
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
                        "disabled": False,
                    },
                )

                user_row = result.fetchone()
                user_id = user_row[0]

                # Insert roles
                if user_data.roles:
                    for role in user_data.roles:
                        await session.execute(
                            text_no_prepare(
                                "INSERT INTO user_roles (user_id, role) VALUES (:user_id, :role)"
                            ),
                            {"user_id": user_id, "role": role},
                        )

                await session.commit()

                # Get user with roles
                user = await self.get_user_by_id(user_id)
                log.info(f"✅ User created: {user.username}")
                return user

            except Exception as e:
                await session.rollback()
                log.error(f"❌ Error creating user: {e}")
                raise

    async def authenticate_user(
        self, username: str, password: str
    ) -> Optional[UserInDB]:
        """Authenticate user with username and password"""
        await self.initialize()

        async with self.db_service.get_session() as session:
            try:
                # Get user with hashed password
                result = await session.execute(
                    text_no_prepare(
                        """
                        SELECT id, username, email, hashed_password, full_name, disabled, created_at, updated_at
                        FROM users 
                        WHERE username = :username AND disabled = FALSE
                    """
                    ),
                    {"username": username},
                )

                user_row = result.fetchone()
                if not user_row:
                    return None

                # Verify password
                if not verify_password(password, user_row[3]):
                    return None

                # Get user roles
                result = await session.execute(
                    text_no_prepare(
                        "SELECT role FROM user_roles WHERE user_id = :user_id"
                    ),
                    {"user_id": user_row[0]},
                )
                roles = [row[0] for row in result.fetchall()]

                return UserInDB(
                    id=user_row[0],
                    username=user_row[1],
                    email=user_row[2],
                    hashed_password=user_row[3],
                    full_name=user_row[4],
                    disabled=user_row[5],
                    roles=roles,
                    scopes=roles,  # For compatibility
                    created_at=user_row[6],
                    updated_at=user_row[7],
                )

            except Exception as e:
                log.error(f"❌ Error authenticating user: {e}")
                return None

    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get user by username"""
        await self.initialize()

        async with self.db_service.get_session() as session:
            try:
                result = await session.execute(
                    text_no_prepare(
                        """
                        SELECT id, username, email, full_name, disabled, created_at, updated_at
                        FROM users 
                        WHERE username = :username
                    """
                    ),
                    {"username": username},
                )

                user_row = result.fetchone()
                if not user_row:
                    return None

                # Get roles
                result = await session.execute(
                    text_no_prepare(
                        "SELECT role FROM user_roles WHERE user_id = :user_id"
                    ),
                    {"user_id": user_row[0]},
                )
                roles = [row[0] for row in result.fetchall()]

                return UserInDB(
                    id=user_row[0],
                    username=user_row[1],
                    email=user_row[2],
                    full_name=user_row[3],
                    disabled=user_row[4],
                    roles=roles,
                    scopes=roles,
                    created_at=user_row[5],
                    updated_at=user_row[6],
                )

            except Exception as e:
                log.error(f"❌ Error getting user by username: {e}")
                return None

    async def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        """Get user by ID"""
        await self.initialize()

        async with self.db_service.get_session() as session:
            try:
                result = await session.execute(
                    text_no_prepare(
                        """
                        SELECT id, username, email, full_name, disabled, created_at, updated_at
                        FROM users 
                        WHERE id = :user_id
                    """
                    ),
                    {"user_id": user_id},
                )

                user_row = result.fetchone()
                if not user_row:
                    return None

                # Get roles
                result = await session.execute(
                    text_no_prepare(
                        "SELECT role FROM user_roles WHERE user_id = :user_id"
                    ),
                    {"user_id": user_id},
                )
                roles = [row[0] for row in result.fetchall()]

                return UserInDB(
                    id=user_row[0],
                    username=user_row[1],
                    email=user_row[2],
                    full_name=user_row[3],
                    disabled=user_row[4],
                    roles=roles,
                    scopes=roles,
                    created_at=user_row[5],
                    updated_at=user_row[6],
                )

            except Exception as e:
                log.error(f"❌ Error getting user by ID: {e}")
                return None

    async def update_user(
        self, user_id: int, user_data: UserUpdate
    ) -> Optional[UserInDB]:
        """Update user information"""
        await self.initialize()

        async with self.db_service.get_session() as session:
            try:
                # Check if user exists
                existing_user = await self.get_user_by_id(user_id)
                if not existing_user:
                    return None

                # Build update query
                update_fields = []
                params = {"user_id": user_id}

                if user_data.email is not None:
                    # Check if email already exists for another user
                    result = await session.execute(
                        text_no_prepare(
                            "SELECT id FROM users WHERE email = :email AND id != :user_id"
                        ),
                        {"email": user_data.email, "user_id": user_id},
                    )
                    if result.fetchone():
                        raise ValueError(f"Email '{user_data.email}' already exists")

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
                    await session.execute(text_no_prepare(query), params)

                # Update roles if provided
                if user_data.roles is not None:
                    # Delete existing roles
                    await session.execute(
                        text_no_prepare(
                            "DELETE FROM user_roles WHERE user_id = :user_id"
                        ),
                        {"user_id": user_id},
                    )

                    # Insert new roles
                    for role in user_data.roles:
                        await session.execute(
                            text_no_prepare(
                                "INSERT INTO user_roles (user_id, role) VALUES (:user_id, :role)"
                            ),
                            {"user_id": user_id, "role": role},
                        )

                await session.commit()

                # Return updated user
                updated_user = await self.get_user_by_id(user_id)
                log.info(f"✅ User updated: {updated_user.username}")
                return updated_user

            except Exception as e:
                await session.rollback()
                log.error(f"❌ Error updating user: {e}")
                raise

    async def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        await self.initialize()

        async with self.db_service.get_session() as session:
            try:
                # Check if user exists
                existing_user = await self.get_user_by_id(user_id)
                if not existing_user:
                    return False

                # Delete user (roles will be deleted automatically due to CASCADE)
                result = await session.execute(
                    text_no_prepare("DELETE FROM users WHERE id = :user_id"),
                    {"user_id": user_id},
                )

                await session.commit()

                deleted = result.rowcount > 0
                if deleted:
                    log.info(f"✅ User deleted: {existing_user.username}")

                return deleted

            except Exception as e:
                await session.rollback()
                log.error(f"❌ Error deleting user: {e}")
                raise

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """List all users with pagination"""
        await self.initialize()

        async with self.db_service.get_session() as session:
            try:
                result = await session.execute(
                    text_no_prepare(
                        """
                        SELECT id, username, email, full_name, disabled, created_at, updated_at
                        FROM users 
                        ORDER BY created_at DESC
                        OFFSET :skip LIMIT :limit
                    """
                    ),
                    {"skip": skip, "limit": limit},
                )

                users = []
                for row in result.fetchall():
                    # Get roles for each user
                    roles_result = await session.execute(
                        text_no_prepare(
                            "SELECT role FROM user_roles WHERE user_id = :user_id"
                        ),
                        {"user_id": row[0]},
                    )
                    roles = [r[0] for r in roles_result.fetchall()]

                    user = UserResponse(
                        id=row[0],
                        username=row[1],
                        email=row[2],
                        full_name=row[3],
                        disabled=row[4],
                        roles=roles,
                        created_at=row[5],
                        updated_at=row[6],
                    )
                    users.append(user)

                return users

            except Exception as e:
                log.error(f"❌ Error listing users: {e}")
                raise

    async def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password"""
        await self.initialize()

        async with self.db_service.get_session() as session:
            try:
                # Hash new password
                hashed_password = get_password_hash(new_password)

                # Update password
                result = await session.execute(
                    text_no_prepare(
                        """
                        UPDATE users 
                        SET hashed_password = :hashed_password, updated_at = NOW()
                        WHERE id = :user_id
                    """
                    ),
                    {"hashed_password": hashed_password, "user_id": user_id},
                )

                await session.commit()

                success = result.rowcount > 0
                if success:
                    log.info(f"✅ Password changed for user ID: {user_id}")

                return success

            except Exception as e:
                await session.rollback()
                log.error(f"❌ Error changing password: {e}")
                raise

    async def get_user_stats(self) -> dict:
        """Get user statistics"""
        await self.initialize()

        async with self.db_service.get_session() as session:
            try:
                # Total users
                result = await session.execute(
                    text_no_prepare("SELECT COUNT(*) FROM users")
                )
                total_users = result.fetchone()[0]

                # Active users
                result = await session.execute(
                    text_no_prepare("SELECT COUNT(*) FROM users WHERE disabled = FALSE")
                )
                active_users = result.fetchone()[0]

                # Users by role
                result = await session.execute(
                    text_no_prepare(
                        """
                        SELECT role, COUNT(*) 
                        FROM user_roles 
                        GROUP BY role 
                        ORDER BY COUNT(*) DESC
                    """
                    )
                )
                roles_stats = {row[0]: row[1] for row in result.fetchall()}

                return {
                    "total_users": total_users,
                    "active_users": active_users,
                    "disabled_users": total_users - active_users,
                    "roles_stats": roles_stats,
                }

            except Exception as e:
                log.error(f"❌ Error getting user stats: {e}")
                raise


# Global async user service instance
_async_user_service = None


async def get_async_user_service() -> AsyncUserService:
    """Get or create async user service instance"""
    global _async_user_service

    if _async_user_service is None:
        _async_user_service = AsyncUserService()
        await _async_user_service.initialize()
        await _async_user_service.create_tables()

    return _async_user_service

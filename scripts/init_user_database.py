"""
Database initialization and migration script for user management
Creates users and user_roles tables and seed initial admin user
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.user_service import get_user_service
from src.models.user import UserCreate
from src.utils.logger import log


def init_user_database():
    """Initialize user database tables and create default admin user"""

    log.info("=" * 60)
    log.info("Starting User Database Initialization")
    log.info("=" * 60)

    try:
        # Get user service
        user_service = get_user_service()

        # Step 1: Create tables
        log.info("\n[Step 1/3] Creating database tables...")
        user_service.create_tables()
        log.info("✅ Tables created successfully")

        # Step 2: Check if admin user exists
        log.info("\n[Step 2/3] Checking for existing users...")
        existing_admin = user_service.get_user_by_username("admin")

        if existing_admin:
            log.info("⚠️  Admin user already exists, skipping creation")
        else:
            # Step 3: Create default admin user
            log.info("\n[Step 3/3] Creating default admin user...")
            admin_data = UserCreate(
                username="admin",
                email="admin@example.com",
                password="Admin123",  # Strong password meeting requirements
                full_name="System Administrator",
                disabled=False,
                roles=["admin", "user"],
            )

            admin_user = user_service.create_user(admin_data)
            log.info(f"✅ Admin user created: {admin_user.username}")
            log.info(f"   Email: {admin_user.email}")
            log.info(f"   Roles: {admin_user.roles}")

        # Create default regular user
        existing_user = user_service.get_user_by_username("user")

        if not existing_user:
            log.info("\nCreating default regular user...")
            user_data = UserCreate(
                username="user",
                email="user@example.com",
                password="User1234",  # 8 characters minimum
                full_name="Regular User",
                disabled=False,
                roles=["user"],
            )

            regular_user = user_service.create_user(user_data)
            log.info(f"✅ Regular user created: {regular_user.username}")
            log.info(f"   Email: {regular_user.email}")
            log.info(f"   Roles: {regular_user.roles}")
        else:
            log.info("⚠️  Regular user already exists, skipping creation")

        # Summary
        users, total = user_service.list_users(skip=0, limit=100)

        log.info("\n" + "=" * 60)
        log.info("DATABASE INITIALIZATION COMPLETE")
        log.info("=" * 60)
        log.info("\n📊 Summary:")
        log.info(f"   Total Users: {total}")
        log.info("\n👥 Users:")

        for user in users:
            status = "🔴 Disabled" if user.disabled else "🟢 Active"
            log.info(f"   - {user.username} ({status})")
            log.info(f"     Email: {user.email}")
            log.info(f"     Roles: {', '.join(user.roles)}")
            log.info(f"     Created: {user.created_at}")

        log.info("\n" + "=" * 60)
        log.info("🔐 DEFAULT LOGIN CREDENTIALS")
        log.info("=" * 60)
        log.info("\nAdmin Account:")
        log.info("  Username: admin")
        log.info("  Password: Admin123")
        log.info("  Roles: admin, user")
        log.info("\nRegular User Account:")
        log.info("  Username: user")
        log.info("  Password: User123")
        log.info("  Roles: user")
        log.info("\n⚠️  IMPORTANT: Change these passwords in production!")
        log.info("=" * 60)

        return True

    except Exception as e:
        log.error(f"\n❌ Database initialization failed: {e}")
        import traceback

        log.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = init_user_database()

    if success:
        print("\n✅ User database initialized successfully!")
        print("\nYou can now:")
        print("  1. Start the server: python main.py")
        print("  2. Login at: POST /auth/login")
        print("  3. Manage users at: /api/users/admin/*")
        print("\n📚 API Documentation: http://localhost:8000/docs")
        sys.exit(0)
    else:
        print("\n❌ Database initialization failed. Check logs for details.")
        sys.exit(1)

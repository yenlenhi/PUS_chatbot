"""
User Management API Routes
Protected admin endpoints for managing users
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from src.models.user import (
    UserCreate,
    UserUpdate,
    UserChangePassword,
    UserResponse,
    UserListResponse,
    UserInDB,
)
from src.services.user_service import get_user_service, UserService
from src.auth import get_current_user
from src.utils.logger import log

# Use UserInDB as the User type for dependency injection
User = UserInDB


# Create router
user_router = APIRouter(prefix="/api/users", tags=["User Management"])


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require admin access"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    if "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


# ============================================
# Public / Self-Service Endpoints
# ============================================


@user_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get current logged-in user information

    Requires authentication
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    user = user_service.get_user_by_username(current_user.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled,
        roles=user.roles,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@user_router.post("/change-password")
async def change_own_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Change own password

    Requires authentication
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    try:
        # Get user ID from username
        user = user_service.get_user_by_username(current_user.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        success = user_service.change_password(
            user_id=user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password change failed"
            )

        return {"message": "Password changed successfully"}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============================================
# Admin Endpoints
# ============================================


@user_router.post(
    "/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate,
    admin_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    """
    Create a new user

    Requires admin access
    """
    try:
        user = user_service.create_user(user_data)
        log.info(f"Admin {admin_user.username} created user: {user.username}")
        return user

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )


@user_router.get("/admin/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    disabled: Optional[bool] = Query(None, description="Filter by disabled status"),
    admin_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    """
    List all users with pagination

    Requires admin access
    """
    skip = (page - 1) * page_size
    users, total = user_service.list_users(
        skip=skip, limit=page_size, disabled=disabled
    )

    return UserListResponse(total=total, users=users, page=page, page_size=page_size)


@user_router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get user details by ID

    Requires admin access
    """
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    return user


@user_router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    admin_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update user information

    Requires admin access
    """
    try:
        user = user_service.update_user(user_id, user_data)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        log.info(f"Admin {admin_user.username} updated user ID: {user_id}")
        return user

    except Exception as e:
        log.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        )


@user_router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    """
    Delete user (soft delete - sets disabled=True)

    Requires admin access
    """
    # Prevent self-deletion
    user = user_service.get_user_by_username(admin_user.username)
    if user and user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    success = user_service.delete_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    log.info(f"Admin {admin_user.username} deleted user ID: {user_id}")
    return {"message": f"User {user_id} has been disabled"}


@user_router.post("/admin/users/{user_id}/enable")
async def enable_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    """
    Enable a disabled user

    Requires admin access
    """
    user_data = UserUpdate(disabled=False)
    user = user_service.update_user(user_id, user_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    log.info(f"Admin {admin_user.username} enabled user ID: {user_id}")
    return {"message": f"User {user_id} has been enabled"}


@user_router.get("/admin/stats")
async def get_user_stats(
    admin_user: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get user statistics

    Requires admin access
    """
    # Get all users
    all_users, total = user_service.list_users(skip=0, limit=10000)

    # Get active users
    active_users, active_count = user_service.list_users(
        skip=0, limit=10000, disabled=False
    )

    # Get disabled users
    disabled_users, disabled_count = user_service.list_users(
        skip=0, limit=10000, disabled=True
    )

    # Count by role
    role_counts = {}
    for user in all_users:
        for role in user.roles:
            role_counts[role] = role_counts.get(role, 0) + 1

    return {
        "total_users": total,
        "active_users": active_count,
        "disabled_users": disabled_count,
        "users_by_role": role_counts,
    }

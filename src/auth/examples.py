"""
Example: How to protect an endpoint with JWT authentication
"""

from fastapi import Depends, HTTPException, status
from src.auth.jwt_handler import get_current_user, User


# Example 1: Optional authentication
async def optional_auth_endpoint(current_user: User = Depends(get_current_user)):
    """
    Endpoint that works with or without authentication
    """
    if current_user:
        return {"message": f"Hello {current_user.username}", "authenticated": True}
    else:
        return {"message": "Hello guest", "authenticated": False}


# Example 2: Required authentication
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    """
    Endpoint that requires authentication
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"message": f"Protected data for {current_user.username}"}


# Example 3: Admin-only endpoint
def require_admin(current_user: User = Depends(get_current_user)):
    """
    Dependency to require admin access
    """
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


async def admin_endpoint(admin_user: User = Depends(require_admin)):
    """
    Endpoint that requires admin privileges
    """
    return {"message": f"Admin panel for {admin_user.username}"}


# Example 4: Custom scope check
def require_scope(required_scope: str):
    """
    Factory function to create scope dependency
    """

    def scope_checker(current_user: User = Depends(get_current_user)):
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        if required_scope not in current_user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Scope '{required_scope}' required",
            )

        return current_user

    return scope_checker


# Usage in route
async def custom_scope_endpoint(user: User = Depends(require_scope("documents:write"))):
    """
    Endpoint that requires specific scope
    """
    return {"message": f"User {user.username} can write documents"}

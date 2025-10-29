"""
Role-Based Access Control (RBAC) implementation
"""
from typing import List
from fastapi import HTTPException, status, Depends
from core.security.auth import get_current_user

# Permission definitions
PERMISSIONS = {
    "conversations:read": ["admin", "user", "viewer"],
    "conversations:write": ["admin", "user"],
    "conversations:delete": ["admin"],
    "users:read": ["admin"],
    "users:write": ["admin"],
    "users:delete": ["admin"],
    "tenants:read": ["admin"],
    "tenants:write": ["admin"],
    "audit:read": ["admin"],
    "api_keys:read": ["admin", "user"],
    "api_keys:write": ["admin", "user"],
    "api_keys:delete": ["admin"],
}


def require_permission(permission: str):
    """
    Dependency factory for requiring specific permission
    Usage: Depends(require_permission("conversations:read"))
    """
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user["role"]
        
        if permission not in PERMISSIONS:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Permission {permission} not defined"
            )
        
        if user_role not in PERMISSIONS[permission]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} requires one of {PERMISSIONS[permission]}"
            )
        
        return current_user
    
    return permission_checker


def require_role(allowed_roles: List[str]):
    """
    Dependency factory for requiring specific role(s)
    Usage: Depends(require_role(["admin"]))
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user["role"]
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: requires one of {allowed_roles}"
            )
        
        return current_user
    
    return role_checker


def check_permission(user_role: str, permission: str) -> bool:
    """Check if a user role has a specific permission"""
    if permission not in PERMISSIONS:
        return False
    return user_role in PERMISSIONS[permission]


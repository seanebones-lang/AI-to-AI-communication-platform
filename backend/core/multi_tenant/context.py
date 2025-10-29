"""
Multi-tenant context management
"""
from typing import Optional
from uuid import UUID
import asyncio
from contextvars import ContextVar
from fastapi import Request, HTTPException, status

# Context variable for tenant_id
tenant_context: ContextVar[Optional[UUID]] = ContextVar('tenant_id', default=None)
user_context: ContextVar[Optional[UUID]] = ContextVar('user_id', default=None)


def get_current_tenant_id() -> Optional[UUID]:
    """Get current tenant ID from context"""
    return tenant_context.get()


def set_current_tenant_id(tenant_id: UUID) -> None:
    """Set current tenant ID in context"""
    tenant_context.set(tenant_id)


def get_current_user_id() -> Optional[UUID]:
    """Get current user ID from context"""
    return user_context.get()


def set_current_user_id(user_id: UUID) -> None:
    """Set current user ID in context"""
    user_context.set(user_id)


def get_tenant_from_request(request: Request) -> Optional[str]:
    """
    Extract tenant identifier from request
    Supports:
    1. X-Tenant-ID header
    2. tenant subdomain (e.g., tenant1.example.com)
    3. Query parameter ?tenant=tenant-id
    """
    # Check header first
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        return tenant_id
    
    # Check subdomain
    host = request.headers.get("host", "")
    if "." in host:
        subdomain = host.split(".")[0]
        # Skip common subdomains
        if subdomain not in ["www", "api", "app"]:
            return subdomain
    
    # Check query parameter
    tenant_id = request.query_params.get("tenant")
    if tenant_id:
        return tenant_id
    
    return None


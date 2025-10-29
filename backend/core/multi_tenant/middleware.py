"""
Multi-tenant middleware for tenant isolation
"""
from typing import Callable, Optional
from uuid import UUID
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from core.multi_tenant.context import (
    set_current_tenant_id,
    get_tenant_from_request,
    set_current_user_id
)
from core.security.auth import decode_token
from database.session import get_db_session
from database.repositories import TenantRepository


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and validate tenant context from requests
    Sets tenant_id in context for all requests
    """
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable
    ):
        # Skip tenant validation for certain paths
        skip_paths = ["/health", "/ready", "/docs", "/openapi.json", "/redoc"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Try to get tenant from request
        tenant_identifier = get_tenant_from_request(request)
        
        # If tenant identifier provided, validate it
        if tenant_identifier:
            # For production, you'd look up tenant by identifier
            # For now, we'll extract from JWT token if available
            tenant_id = await self._get_tenant_id_from_token(request)
            if not tenant_id:
                # Could also validate against tenant identifier
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tenant identifier"
                )
            set_current_tenant_id(tenant_id)
        
        response = await call_next(request)
        return response
    
    async def _get_tenant_id_from_token(self, request: Request) -> Optional[UUID]:
        """Extract tenant_id from JWT token if present"""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        try:
            token = authorization.replace("Bearer ", "")
            payload = decode_token(token)
            tenant_id_str = payload.get("tenant_id")
            if tenant_id_str:
                return UUID(tenant_id_str)
        except Exception:
            pass
        
        return None


async def get_current_tenant(
    request: Request,
    db: AsyncSession
) -> dict:
    """
    Dependency to get current tenant from context
    Raises 403 if tenant not found or inactive
    """
    from core.multi_tenant.context import get_current_tenant_id
    from database.repositories import TenantRepository
    
    tenant_id = get_current_tenant_id()
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant context required"
        )
    
    tenant_repo = TenantRepository(db)
    tenant = await tenant_repo.get_by_id(tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant is inactive"
        )
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "tier": tenant.tier,
        "config": tenant.config,
        "limits": tenant.limits,
        "feature_flags": tenant.feature_flags
    }


"""
Repository for Tenant model
"""
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from models.db_models import Tenant


class TenantRepository(BaseRepository[Tenant]):
    """Repository for Tenant operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Tenant, session)
    
    async def get_by_name(self, name: str) -> Optional[Tenant]:
        """Get tenant by name"""
        result = await self.session.execute(
            select(Tenant).where(Tenant.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_active_tenants(self) -> list[Tenant]:
        """Get all active tenants"""
        result = await self.session.execute(
            select(Tenant).where(Tenant.is_active == True)
        )
        return list(result.scalars().all())


"""
Repository for User model
"""
from typing import Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from models.db_models import User


class UserRepository(BaseRepository[User]):
    """Repository for User operations with tenant isolation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_email(
        self, 
        email: str, 
        tenant_id: Optional[UUID] = None
    ) -> Optional[User]:
        """Get user by email, optionally scoped to tenant"""
        stmt = select(User).where(User.email == email)
        
        if tenant_id:
            stmt = stmt.where(User.tenant_id == tenant_id)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_tenant(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """Get all users for a tenant"""
        result = await self.session.execute(
            select(User)
            .where(User.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


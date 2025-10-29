"""
Repository for Conversation model
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from models.db_models import Conversation, Message


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for Conversation operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Conversation, session)
    
    async def get_by_session_id(
        self, 
        session_id: str, 
        tenant_id: UUID
    ) -> Optional[Conversation]:
        """Get conversation by session_id scoped to tenant"""
        result = await self.session.execute(
            select(Conversation)
            .where(
                and_(
                    Conversation.session_id == session_id,
                    Conversation.tenant_id == tenant_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_tenant(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Conversation]:
        """Get all conversations for a tenant"""
        stmt = (
            select(Conversation)
            .where(Conversation.tenant_id == tenant_id)
        )
        
        if status:
            stmt = stmt.where(Conversation.status == status)
        
        stmt = stmt.order_by(Conversation.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_user(
        self,
        user_id: UUID,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Conversation]:
        """Get all conversations for a user within a tenant"""
        result = await self.session.execute(
            select(Conversation)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.tenant_id == tenant_id
                )
            )
            .order_by(Conversation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


"""
Repository for Message model
"""
from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from models.db_models import Message


class MessageRepository(BaseRepository[Message]):
    """Repository for Message operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Message, session)
    
    async def get_by_conversation(
        self,
        conversation_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get all messages for a conversation, ordered by timestamp"""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_latest_by_conversation(
        self,
        conversation_id: UUID,
        limit: int = 10
    ) -> List[Message]:
        """Get latest N messages for a conversation"""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


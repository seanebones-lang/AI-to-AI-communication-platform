"""
Repository for AIResponse model for cost tracking
"""
from typing import List
from uuid import UUID
from datetime import datetime, date
from sqlalchemy import select, and_, func, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from models.db_models import AIResponse


class AIResponseRepository(BaseRepository[AIResponse]):
    """Repository for AIResponse operations with cost tracking"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(AIResponse, session)
    
    async def get_by_conversation(
        self,
        conversation_id: UUID
    ) -> List[AIResponse]:
        """Get all AI responses for a conversation"""
        result = await self.session.execute(
            select(AIResponse)
            .where(AIResponse.conversation_id == conversation_id)
            .order_by(AIResponse.created_at.asc())
        )
        return list(result.scalars().all())
    
    async def get_cost_by_tenant(
        self,
        tenant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """Get aggregated cost metrics for a tenant"""
        stmt = (
            select(
                func.sum(AIResponse.cost_usd).label("total_cost"),
                func.count(AIResponse.id).label("total_requests")
            )
            .where(AIResponse.tenant_id == tenant_id)
            .where(AIResponse.success == True)
        )
        
        if start_date:
            stmt = stmt.where(func.date(AIResponse.created_at) >= start_date)
        
        if end_date:
            stmt = stmt.where(func.date(AIResponse.created_at) <= end_date)
        
        result = await self.session.execute(stmt)
        row = result.first()
        
        return {
            "total_cost": float(row.total_cost or 0),
            "total_requests": row.total_requests or 0
        }
    
    async def get_by_tenant_date_range(
        self,
        tenant_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[AIResponse]:
        """Get AI responses for tenant within date range"""
        result = await self.session.execute(
            select(AIResponse)
            .where(
                and_(
                    AIResponse.tenant_id == tenant_id,
                    func.date(AIResponse.created_at) >= start_date,
                    func.date(AIResponse.created_at) <= end_date
                )
            )
            .order_by(AIResponse.created_at.desc())
        )
        return list(result.scalars().all())


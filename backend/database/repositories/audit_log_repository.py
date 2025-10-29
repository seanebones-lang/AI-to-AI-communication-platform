"""
Repository for AuditLog model
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from models.db_models import AuditLog


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for AuditLog operations with tenant isolation"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(AuditLog, session)
    
    async def get_by_tenant(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Get audit logs for a tenant with optional filters"""
        stmt = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
        )
        
        if event_type:
            stmt = stmt.where(AuditLog.event_type == event_type)
        
        if start_date:
            stmt = stmt.where(AuditLog.timestamp >= start_date)
        
        if end_date:
            stmt = stmt.where(AuditLog.timestamp <= end_date)
        
        stmt = stmt.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_session(
        self,
        session_id: str,
        tenant_id: UUID
    ) -> List[AuditLog]:
        """Get audit logs for a specific session scoped to tenant"""
        result = await self.session.execute(
            select(AuditLog)
            .where(
                and_(
                    AuditLog.session_id == session_id,
                    AuditLog.tenant_id == tenant_id
                )
            )
            .order_by(desc(AuditLog.timestamp))
        )
        return list(result.scalars().all())


"""
Base repository with common database operations
"""
from typing import Generic, TypeVar, Optional, List, Type
from uuid import UUID
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_with_relationships(
        self, 
        id: UUID, 
        *relationships: str
    ) -> Optional[ModelType]:
        """Get entity by ID with eager loaded relationships to avoid N+1 queries"""
        stmt = select(self.model).where(self.model.id == id)
        if relationships:
            stmt = stmt.options(*[selectinload(getattr(self.model, rel)) for rel in relationships])
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> List[ModelType]:
        """Get all entities with pagination and optional filters"""
        stmt = select(self.model)
        
        if filters:
            conditions = [getattr(self.model, key) == value for key, value in filters.items()]
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def create(self, **kwargs) -> ModelType:
        """Create a new entity"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
    
    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        """Update an entity by ID"""
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()
    
    async def delete(self, id: UUID) -> bool:
        """Delete an entity by ID"""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
    
    async def count(self, filters: Optional[dict] = None) -> int:
        """Count entities matching optional filters"""
        stmt = select(func.count()).select_from(self.model)
        
        if filters:
            conditions = [getattr(self.model, key) == value for key, value in filters.items()]
            stmt = stmt.where(and_(*conditions))
        
        result = await self.session.execute(stmt)
        return result.scalar_one()


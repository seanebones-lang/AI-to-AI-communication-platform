"""
Database session management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from .base import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


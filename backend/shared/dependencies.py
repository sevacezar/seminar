"""
Зависимости FastAPI
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

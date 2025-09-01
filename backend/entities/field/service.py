"""
Сервис для работы с месторождениями
"""
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.shared.base_service import BaseService
from backend.entities.field.model import Field
from backend.core.exceptions import AlreadyExistsError
from backend.core.logging import get_logger

logger = get_logger(__name__)


class FieldService(BaseService[Field]):
    """Сервис для работы с месторождениями"""
    
    def __init__(self):
        super().__init__(Field)
    
    async def create(
        self,
        db: AsyncSession,
        obj_data: Dict[str, Any],
        **kwargs
    ) -> Field:
        """Создание нового месторождения с проверкой уникальности имени"""
        
        # Проверка уникальности имени
        existing = await self.get_by_name(db, obj_data["name"])
        if existing:
            raise AlreadyExistsError(f"Field with name '{obj_data['name']}' already exists")
        
        return await super().create(db, obj_data, **kwargs)
    
    async def get_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[Field]:
        """Получение месторождения по имени"""
        query = select(Field).where(Field.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_operator(
        self,
        db: AsyncSession,
        operator: str,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Field], int]:
        """Получение месторождений по оператору"""
        filters = {"operator": operator}
        return await self.get_multi(db, limit=limit, offset=offset, filters=filters)


# Глобальный экземпляр сервиса
field_service = FieldService()

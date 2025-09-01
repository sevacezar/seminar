"""
Сервис для работы с объектами разработки
"""
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.base_service import BaseService
from backend.entities.development_object.model import DevelopmentObject
from backend.shared.enums import SedimentComplexEnum

logger = logging.getLogger(__name__)


class DevelopmentObjectService(BaseService[DevelopmentObject]):
    """Сервис для работы с объектами разработки"""
    
    def __init__(self):
        super().__init__(DevelopmentObject)
    
    async def get_by_field_id(
        self,
        db: AsyncSession,
        field_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[DevelopmentObject], int]:
        """Получение объектов разработки по ID месторождения"""
        filters = {"field_id": field_id}
        return await self.get_multi(db, limit=limit, offset=offset, filters=filters)
    
    async def get_by_sediment_complex(
        self,
        db: AsyncSession,
        sediment_complex: SedimentComplexEnum,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[DevelopmentObject], int]:
        """Получение объектов разработки по комплексу отложений"""
        filters = {"sediment_complex": sediment_complex}
        return await self.get_multi(db, limit=limit, offset=offset, filters=filters)


# Глобальный экземпляр сервиса
development_object_service = DevelopmentObjectService()

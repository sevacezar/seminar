"""
Сервис для работы с флюидами
"""
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.base_service import BaseService
from backend.entities.fluid.model import Fluid
from backend.shared.enums import FluidTypeEnum

logger = logging.getLogger(__name__)


class FluidService(BaseService[Fluid]):
    """Сервис для работы с флюидами"""
    
    def __init__(self):
        super().__init__(Fluid)
    
    async def get_by_development_object_id(
        self,
        db: AsyncSession,
        development_object_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Fluid], int]:
        """Получение флюидов по ID объекта разработки"""
        filters = {"development_object_id": development_object_id}
        return await self.get_multi(db, limit=limit, offset=offset, filters=filters)
    
    async def get_by_fluid_type(
        self,
        db: AsyncSession,
        fluid_type: FluidTypeEnum,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Fluid], int]:
        """Получение флюидов по типу"""
        filters = {"fluid_type": fluid_type}
        return await self.get_multi(db, limit=limit, offset=offset, filters=filters)


# Глобальный экземпляр сервиса
fluid_service = FluidService()

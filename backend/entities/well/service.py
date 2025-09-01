"""
Сервис для работы со скважинами
"""
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.base_service import BaseService
from backend.entities.well.model import Well
from backend.shared.enums import FluidTypeEnum

logger = logging.getLogger(__name__)


class WellService(BaseService[Well]):
    """Сервис для работы со скважинами"""
    
    def __init__(self):
        super().__init__(Well)
    
    async def get_by_field_id(
        self,
        db: AsyncSession,
        field_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Well], int]:
        """Получение скважин по ID месторождения"""
        filters = {"field_id": field_id}
        return await self.get_multi(db, limit=limit, offset=offset, filters=filters)
    
    async def get_by_fluid_type(
        self,
        db: AsyncSession,
        fluid_type: FluidTypeEnum,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Well], int]:
        """Получение скважин по типу флюида"""
        filters = {"fluid_type": fluid_type}
        return await self.get_multi(db, limit=limit, offset=offset, filters=filters)


# Глобальный экземпляр сервиса
well_service = WellService()

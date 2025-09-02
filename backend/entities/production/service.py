"""
Сервис для работы с записями добычи
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from backend.shared.base_service import BaseService
from backend.entities.production.model import Production
from backend.shared.enums import FluidTypeEnum, UnitEnum

logger = logging.getLogger(__name__)


class ProductionService(BaseService[Production]):
    """Сервис для работы с записями добычи"""
    
    def __init__(self):
        super().__init__(Production)
    
    async def get_by_date_range(
        self,
        db: AsyncSession,
        date_from: date,
        date_to: date,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Production], int]:
        """Получение записей добычи за период"""
        query = select(self.model).where(
            and_(
                self.model.date >= date_from,
                self.model.date <= date_to
            )
        )
        
        count_query = select(func.count(self.model.id)).where(
            and_(
                self.model.date >= date_from,
                self.model.date <= date_to
            )
        )
        
        # Пагинация
        query = query.offset(offset).limit(limit)
        
        # Выполнение запросов
        result = await db.execute(query)
        items = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return list(items), total
    
    async def get_by_well_id(
        self,
        db: AsyncSession,
        well_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Production], int]:
        """Получение записей добычи по ID скважины"""
        filters = {"well_id": well_id}
        return await self.get_multi(db, limit=limit, offset=offset, filters=filters)
    
    async def get_by_field_id(
        self,
        db: AsyncSession,
        field_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Production], int]:
        """Получение записей добычи по ID месторождения"""
        filters = {"field_id": field_id}
        return await self.get_multi(db, limit=limit, offset=offset, filters=filters)
    
    async def get_by_fluid_type(
        self,
        db: AsyncSession,
        fluid_type: FluidTypeEnum,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Production], int]:
        """Получение записей добычи по типу флюида"""
        filters = {"fluid_type": fluid_type}
        return await self.get_multi(db, limit=limit, offset=offset, filters=filters)


# Глобальный экземпляр сервиса
production_service = ProductionService()

"""
FastAPI роутер для аналитических операций
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status

from backend.core.logging import get_logger
from backend.shared.dependencies import get_db
from backend.entities.analytics.service import analytics_service
from backend.entities.analytics.schema import ProductionDynamicsResponseSchema
from backend.shared.enums import SedimentComplexEnum, FluidTypeEnum, AggregationStepEnum
from backend.core.exceptions import (
    ValidationError,
    validation_exception,
    not_found_exception,
    internal_server_exception
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/production/dynamics",
    response_model=ProductionDynamicsResponseSchema,
    summary="Получение динамики добычи по выбранным параметрам"
)
async def get_production_dynamics(
    date_from: date = Query(..., description="Начальная дата (включительно)"),
    date_to: date = Query(..., description="Конечная дата (включительно)"),
    fluid_type: FluidTypeEnum = Query(FluidTypeEnum.GAS, description="Тип флюида"),
    field_ids: Optional[List[int]] = Query(None, description="Список ID месторождений"),
    sediment_complexes: Optional[List[SedimentComplexEnum]] = Query(None, description="Список комплексов отложений"),
    aggregation_step: AggregationStepEnum = Query(AggregationStepEnum.YEARLY, description="Шаг агрегации"),
    db: AsyncSession = Depends(get_db)
) -> ProductionDynamicsResponseSchema:
    """
    Получение динамики добычи по выбранным параметрам
    
    Позволяет:
    - Выбирать период (date_from, date_to включительно)
    - Фильтровать по типу флюида (по умолчанию gas)
    - Выбирать месторождения (по умолчанию все)
    - Фильтровать по комплексам отложений (по умолчанию все)
    - Выбирать шаг агрегации (по умолчанию yearly)
    
    Возвращает данные для построения графиков с накоплением добычи
    по месторождениям для указанного флюида и комплексов.
    """
    try:
        # Валидация параметров
        if date_from > date_to:
            raise validation_exception("date_from must be less than or equal to date_to")
        
        # Валидация enum'ов происходит автоматически через Pydantic
        
        # Получение данных
        result = await analytics_service.get_production_dynamics(
            db=db,
            date_from=date_from,
            date_to=date_to,
            fluid_type=fluid_type,
            field_ids=field_ids,
            sediment_complexes=sediment_complexes,
            aggregation_step=aggregation_step
        )
        
        # Возвращаем результат даже если данных нет (пустой список)
        # Фронтенд сам обработает отсутствие данных
        return result
        
    except ValidationError as e:
        logger.warning(f"Validation error in production dynamics: {str(e)}")
        raise validation_exception(str(e))
    except Exception as e:
        # Проверяем, не является ли это ошибкой валидации, завернутой в исключение
        if "validation_error" in str(e) or "date_from must be less than" in str(e):
            logger.warning(f"Date validation error: {str(e)}")
            raise validation_exception("Некорректный диапазон дат. Конечная дата должна быть больше или равна начальной.")
        logger.error(f"Error getting production dynamics: {str(e)}")
        raise internal_server_exception()

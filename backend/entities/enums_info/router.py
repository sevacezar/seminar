"""
FastAPI роутер для получения информации о доступных enum значениях
"""
from typing import List, Dict
from fastapi import APIRouter

from backend.shared.enums import SedimentComplexEnum, FluidTypeEnum, AggregationStepEnum

router = APIRouter(prefix="/enums", tags=["enums"])


@router.get(
    "/sediment-complexes",
    response_model=List[str],
    summary="Получить список комплексов отложений"
)
async def get_sediment_complexes() -> List[str]:
    """Получение списка доступных комплексов отложений"""
    return SedimentComplexEnum.get_values()


@router.get(
    "/fluid-types",
    response_model=List[str],
    summary="Получить список типов флюидов"
)
async def get_fluid_types() -> List[str]:
    """Получение списка доступных типов флюидов"""
    return FluidTypeEnum.get_values()


@router.get(
    "/aggregation-steps",
    response_model=List[str],
    summary="Получить список шагов агрегации"
)
async def get_aggregation_steps() -> List[str]:
    """Получение списка доступных шагов агрегации для аналитики"""
    return AggregationStepEnum.get_values()


@router.get(
    "/all",
    response_model=Dict[str, List[str]],
    summary="Получить все доступные enum значения"
)
async def get_all_enums() -> Dict[str, List[str]]:
    """Получение всех доступных enum значений одним запросом"""
    return {
        "sediment_complexes": SedimentComplexEnum.get_values(),
        "fluid_types": FluidTypeEnum.get_values(),
        "aggregation_steps": AggregationStepEnum.get_values()
    }

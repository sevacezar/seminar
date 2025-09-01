"""
Pydantic схемы для сущности Флюид (Fluid)
"""
from typing import Optional
from backend.shared.base_schema import BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema
from backend.shared.enums import FluidTypeEnum


class FluidCreateSchema(BaseCreateSchema):
    """Схема для создания флюида"""
    fluid_type: FluidTypeEnum
    development_object_id: int


class FluidUpdateSchema(BaseUpdateSchema):
    """Схема для обновления флюида"""
    fluid_type: Optional[FluidTypeEnum] = None


class FluidResponseSchema(BaseResponseSchema):
    """Схема для ответа с данными флюида"""
    fluid_type: FluidTypeEnum
    development_object_id: int

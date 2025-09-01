"""
Pydantic схемы для сущности Скважина (Well)
"""
from typing import Optional
from backend.shared.base_schema import BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema
from backend.shared.enums import FluidTypeEnum


class WellCreateSchema(BaseCreateSchema):
    """Схема для создания скважины"""
    name: str
    field_id: int
    fluid_type: FluidTypeEnum


class WellUpdateSchema(BaseUpdateSchema):
    """Схема для обновления скважины"""
    name: Optional[str] = None
    fluid_type: Optional[FluidTypeEnum] = None


class WellResponseSchema(BaseResponseSchema):
    """Схема для ответа с данными скважины"""
    name: str
    field_id: int
    fluid_type: FluidTypeEnum

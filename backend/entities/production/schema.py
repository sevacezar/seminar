"""
Pydantic схемы для сущности Добыча (Production)
"""
from datetime import date
from decimal import Decimal
from typing import Optional
from backend.shared.base_schema import BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema
from backend.shared.enums import FluidTypeEnum


class ProductionCreateSchema(BaseCreateSchema):
    """Схема для создания записи добычи"""
    well_id: int
    fluid_id: int
    date: date
    amount: Decimal
    unit: str
    fluid_type: FluidTypeEnum
    field_id: int
    development_object_id: int


class ProductionUpdateSchema(BaseUpdateSchema):
    """Схема для обновления записи добычи"""
    amount: Optional[Decimal] = None
    unit: Optional[str] = None


class ProductionResponseSchema(BaseResponseSchema):
    """Схема для ответа с данными записи добычи"""
    well_id: int
    fluid_id: int
    date: date
    amount: Decimal
    unit: str
    fluid_type: FluidTypeEnum
    field_id: int
    development_object_id: int

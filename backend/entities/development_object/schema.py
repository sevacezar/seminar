"""
Pydantic схемы для сущности Объект разработки (Development Object)
"""
from typing import Optional
from backend.shared.base_schema import BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema
from backend.shared.enums import SedimentComplexEnum


class DevelopmentObjectCreateSchema(BaseCreateSchema):
    """Схема для создания объекта разработки"""
    name: str
    field_id: int
    sediment_complex: SedimentComplexEnum


class DevelopmentObjectUpdateSchema(BaseUpdateSchema):
    """Схема для обновления объекта разработки"""
    name: Optional[str] = None
    sediment_complex: Optional[SedimentComplexEnum] = None


class DevelopmentObjectResponseSchema(BaseResponseSchema):
    """Схема для ответа с данными объекта разработки"""
    name: str
    field_id: int
    sediment_complex: SedimentComplexEnum

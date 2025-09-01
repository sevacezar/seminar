"""
Pydantic схемы для сущности Месторождение (Field)
"""
from typing import Optional
from backend.shared.base_schema import BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema


class FieldCreateSchema(BaseCreateSchema):
    """Схема для создания месторождения"""
    name: str
    operator: str


class FieldUpdateSchema(BaseUpdateSchema):
    """Схема для обновления месторождения"""
    name: Optional[str] = None
    operator: Optional[str] = None


class FieldResponseSchema(BaseResponseSchema):
    """Схема для ответа с данными месторождения"""
    name: str
    operator: str


# Схемы для массовых операций
class FieldBulkCreateSchema(BaseCreateSchema):
    """Схема для массового создания месторождений"""
    fields: list[FieldCreateSchema]

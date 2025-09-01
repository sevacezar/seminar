"""
Базовые классы для Pydantic схем
"""
from datetime import datetime
from typing import Generic, List, TypeVar, Optional
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовая схема с настройками для всех Pydantic моделей"""
    
    model_config = ConfigDict(
        from_attributes=True,  # Для работы с SQLAlchemy моделями
        validate_assignment=True,  # Для валидации присваивания значений
        arbitrary_types_allowed=True  # Для работы с произвольными типами данных
    )


class TimestampMixin(BaseModel):
    """Миксин для добавления временных меток"""
    created_at: datetime
    updated_at: datetime


class BaseCreateSchema(BaseSchema):
    """Базовая схема для создания сущности"""
    pass


class BaseUpdateSchema(BaseSchema):
    """Базовая схема для обновления сущности"""
    pass


class BaseResponseSchema(BaseSchema, TimestampMixin):
    """Базовая схема для ответа с сущностью"""
    id: int


# Типы для generic классов
T = TypeVar('T')


class PaginatedResponse(BaseSchema, Generic[T]):
    """Схема для пагинированных ответов"""
    data: List[T]
    total: int
    limit: int
    offset: int


class BulkCreateResponse(BaseSchema):
    """Схема для ответа на массовое создание (все или никакие)"""
    created: int
    total: int
    ids: List[int]
    processing_time_ms: Optional[int] = None


class ErrorResponse(BaseSchema):
    """Схема для ошибок"""
    error: str
    message: str
    details: Optional[dict] = None

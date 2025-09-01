"""
FastAPI роутер для месторождений
"""
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger
from backend.shared.dependencies import get_db
from backend.shared.base_schema import PaginatedResponse, BulkCreateResponse
from backend.entities.field.service import field_service
from backend.entities.field.schema import (
    FieldCreateSchema,
    FieldUpdateSchema,
    FieldResponseSchema
)
from backend.core.exceptions import (
    NotFoundError,
    AlreadyExistsError,
    ValidationError,
    not_found_exception,
    validation_exception,
    conflict_exception,
    internal_server_exception
)

logger = get_logger(__name__)

router = APIRouter(prefix="/fields", tags=["fields"])


@router.post(
    "/",
    response_model=FieldResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новое месторождение"
)
async def create_field(
    field_data: FieldCreateSchema,
    db: AsyncSession = Depends(get_db)
) -> FieldResponseSchema:
    """Создание нового месторождения"""
    try:
        field = await field_service.create(db, field_data.model_dump())
        return FieldResponseSchema.model_validate(field)
    except AlreadyExistsError as e:
        raise conflict_exception(str(e))
    except ValidationError as e:
        raise validation_exception(str(e))
    except Exception as e:
        logger.error(f"Error creating field: {str(e)}")
        raise internal_server_exception()


@router.get(
    "/",
    response_model=PaginatedResponse[FieldResponseSchema],
    summary="Получить список месторождений"
)
async def get_fields(
    operator: str = None,
    name: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[FieldResponseSchema]:
    """Получение списка месторождений с фильтрацией и пагинацией"""
    try:
        filters = {}
        if operator:
            filters["operator"] = operator
        if name:
            filters["name"] = name
        
        fields, total = await field_service.get_multi(
            db, 
            limit=limit, 
            offset=offset, 
            filters=filters
        )
        
        return PaginatedResponse(
            data=[FieldResponseSchema.model_validate(field) for field in fields],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error getting fields: {str(e)}")
        raise internal_server_exception()


@router.get(
    "/{field_id}",
    response_model=FieldResponseSchema,
    summary="Получить месторождение по ID"
)
async def get_field(
    field_id: int,
    db: AsyncSession = Depends(get_db)
) -> FieldResponseSchema:
    """Получение месторождения по ID"""
    try:
        field = await field_service.get_by_id_or_404(db, field_id)
        return FieldResponseSchema.model_validate(field)
    except NotFoundError:
        raise not_found_exception("Field not found")
    except Exception as e:
        logger.error(f"Error getting field {field_id}: {str(e)}")
        raise internal_server_exception()


@router.patch(
    "/{field_id}",
    response_model=FieldResponseSchema,
    summary="Обновить месторождение"
)
async def update_field(
    field_id: int,
    field_data: FieldUpdateSchema,
    db: AsyncSession = Depends(get_db)
) -> FieldResponseSchema:
    """Частичное обновление месторождения"""
    try:
        # Исключаем None значения
        update_data = field_data.model_dump(exclude_unset=True)
        if not update_data:
            raise validation_exception("No data provided for update")
        
        field = await field_service.update(db, field_id, update_data)
        return FieldResponseSchema.model_validate(field)
    except NotFoundError:
        raise not_found_exception("Field not found")
    except AlreadyExistsError as e:
        raise conflict_exception(str(e))
    except ValidationError as e:
        raise validation_exception(str(e))
    except Exception as e:
        logger.error(f"Error updating field {field_id}: {str(e)}")
        raise internal_server_exception()


@router.delete(
    "/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить месторождение"
)
async def delete_field(
    field_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление месторождения"""
    try:
        await field_service.delete(db, field_id)
    except NotFoundError:
        raise not_found_exception("Field not found")
    except Exception as e:
        logger.error(f"Error deleting field {field_id}: {str(e)}")
        raise internal_server_exception()


@router.post(
    "/bulk",
    response_model=BulkCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Массовое создание месторождений"
)
async def bulk_create_fields(
    fields_data: List[FieldCreateSchema],
    db: AsyncSession = Depends(get_db)
) -> BulkCreateResponse:
    """Массовое создание месторождений - все или никакие"""
    start_time = time.time()
    
    try:
        objects_data = [field.model_dump() for field in fields_data]
        created_objects = await field_service.bulk_create(db, objects_data)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return BulkCreateResponse(
            created=len(created_objects),
            total=len(fields_data),
            ids=[obj.id for obj in created_objects],
            processing_time_ms=processing_time
        )
        
    except ValidationError as e:
        logger.warning(f"Bulk create validation failed: {str(e)}")
        raise validation_exception(str(e), e.details)
    except AlreadyExistsError as e:
        logger.warning(f"Bulk create failed - duplicate found: {str(e)}")
        raise conflict_exception(str(e))
    except Exception as e:
        logger.error(f"Error in bulk create fields: {str(e)}")
        raise internal_server_exception()

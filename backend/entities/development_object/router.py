"""
FastAPI роутер для объектов разработки
"""
import time
from typing import List
from fastapi import APIRouter, Depends, status

from backend.core.logging import get_logger
from backend.shared.dependencies import get_db
from backend.shared.base_schema import PaginatedResponse, BulkCreateResponse
from backend.entities.development_object.service import development_object_service
from backend.entities.development_object.schema import (
    DevelopmentObjectCreateSchema,
    DevelopmentObjectUpdateSchema,
    DevelopmentObjectResponseSchema
)
from backend.shared.enums import SedimentComplexEnum
from backend.core.exceptions import (
    NotFoundError,
    ValidationError,
    not_found_exception,
    validation_exception,
    internal_server_exception
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

router = APIRouter(prefix="/development-objects", tags=["development-objects"])


@router.post(
    "/",
    response_model=DevelopmentObjectResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый объект разработки"
)
async def create_development_object(
    obj_data: DevelopmentObjectCreateSchema,
    db: AsyncSession = Depends(get_db)
) -> DevelopmentObjectResponseSchema:
    """Создание нового объекта разработки"""
    try:
        obj = await development_object_service.create(db, obj_data.model_dump())
        return DevelopmentObjectResponseSchema.model_validate(obj)
    except ValidationError as e:
        raise validation_exception(str(e))
    except Exception as e:
        logger.error(f"Error creating development object: {str(e)}")
        raise internal_server_exception()


@router.get(
    "/",
    response_model=PaginatedResponse[DevelopmentObjectResponseSchema],
    summary="Получить список объектов разработки"
)
async def get_development_objects(
    field_id: int = None,
    sediment_complex: SedimentComplexEnum = None,
    name: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[DevelopmentObjectResponseSchema]:
    """Получение списка объектов разработки с фильтрацией и пагинацией"""
    try:
        filters = {}
        if field_id:
            filters["field_id"] = field_id
        if sediment_complex:
            filters["sediment_complex"] = sediment_complex
        if name:
            filters["name"] = name
        
        objects, total = await development_object_service.get_multi(
            db, 
            limit=limit, 
            offset=offset, 
            filters=filters
        )
        
        return PaginatedResponse(
            data=[DevelopmentObjectResponseSchema.model_validate(obj) for obj in objects],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error getting development objects: {str(e)}")
        raise internal_server_exception()


@router.get(
    "/{obj_id}",
    response_model=DevelopmentObjectResponseSchema,
    summary="Получить объект разработки по ID"
)
async def get_development_object(
    obj_id: int,
    db: AsyncSession = Depends(get_db)
) -> DevelopmentObjectResponseSchema:
    """Получение объекта разработки по ID"""
    try:
        obj = await development_object_service.get_by_id_or_404(db, obj_id)
        return DevelopmentObjectResponseSchema.model_validate(obj)
    except NotFoundError:
        raise not_found_exception("Development object not found")
    except Exception as e:
        logger.error(f"Error getting development object {obj_id}: {str(e)}")
        raise internal_server_exception()


@router.patch(
    "/{obj_id}",
    response_model=DevelopmentObjectResponseSchema,
    summary="Обновить объект разработки"
)
async def update_development_object(
    obj_id: int,
    obj_data: DevelopmentObjectUpdateSchema,
    db: AsyncSession = Depends(get_db)
) -> DevelopmentObjectResponseSchema:
    """Частичное обновление объекта разработки"""
    try:
        update_data = obj_data.model_dump(exclude_unset=True)
        if not update_data:
            raise validation_exception("No data provided for update")
        
        obj = await development_object_service.update(db, obj_id, update_data)
        return DevelopmentObjectResponseSchema.model_validate(obj)
    except NotFoundError:
        raise not_found_exception("Development object not found")
    except ValidationError as e:
        raise validation_exception(str(e))
    except Exception as e:
        logger.error(f"Error updating development object {obj_id}: {str(e)}")
        raise internal_server_exception()


@router.delete(
    "/{obj_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить объект разработки"
)
async def delete_development_object(
    obj_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление объекта разработки"""
    try:
        await development_object_service.delete(db, obj_id)
    except NotFoundError:
        raise not_found_exception("Development object not found")
    except Exception as e:
        logger.error(f"Error deleting development object {obj_id}: {str(e)}")
        raise internal_server_exception()


@router.post(
    "/bulk",
    response_model=BulkCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Массовое создание объектов разработки"
)
async def bulk_create_development_objects(
    objects_data: List[DevelopmentObjectCreateSchema],
    db: AsyncSession = Depends(get_db)
) -> BulkCreateResponse:
    """Массовое создание объектов разработки - все или никакие"""
    start_time = time.time()
    
    try:
        objects_data_dict = [obj.model_dump() for obj in objects_data]
        created_objects = await development_object_service.bulk_create(db, objects_data_dict)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return BulkCreateResponse(
            created=len(created_objects),
            total=len(objects_data),
            ids=[obj.id for obj in created_objects],
            processing_time_ms=processing_time
        )
        
    except ValidationError as e:
        logger.warning(f"Bulk create validation failed: {str(e)}")
        raise validation_exception(str(e), e.details)
    except Exception as e:
        logger.error(f"Error in bulk create development objects: {str(e)}")
        raise internal_server_exception()

"""
FastAPI роутер для записей добычи
"""
import time
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query

from backend.core.logging import get_logger
from backend.shared.dependencies import get_db
from backend.shared.base_schema import PaginatedResponse, BulkCreateResponse
from backend.entities.production.service import production_service
from backend.entities.production.schema import (
    ProductionCreateSchema,
    ProductionUpdateSchema,
    ProductionResponseSchema
)
from backend.shared.enums import FluidTypeEnum
from backend.core.exceptions import (
    NotFoundError,
    ValidationError,
    not_found_exception,
    validation_exception,
    internal_server_exception
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

router = APIRouter(prefix="/production", tags=["production"])


@router.post(
    "/",
    response_model=ProductionResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую запись добычи"
)
async def create_production_record(
    production_data: ProductionCreateSchema,
    db: AsyncSession = Depends(get_db)
) -> ProductionResponseSchema:
    """Создание новой записи добычи"""
    try:
        production = await production_service.create(db, production_data.model_dump())
        return ProductionResponseSchema.model_validate(production)
    except ValidationError as e:
        raise validation_exception(str(e))
    except Exception as e:
        logger.error(f"Error creating production record: {str(e)}")
        raise internal_server_exception()


@router.get(
    "/",
    response_model=PaginatedResponse[ProductionResponseSchema],
    summary="Получить список записей добычи"
)
async def get_production_records(
    well_id: Optional[int] = Query(None),
    fluid_id: Optional[int] = Query(None),
    field_id: Optional[int] = Query(None),
    development_object_id: Optional[int] = Query(None),
    fluid_type: Optional[FluidTypeEnum] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[ProductionResponseSchema]:
    """Получение списка записей добычи с фильтрацией и пагинацией"""
    try:
        # Если указан диапазон дат, используем специальный метод
        if date_from and date_to:
            records, total = await production_service.get_by_date_range(
                db, date_from, date_to, limit, offset
            )
        else:
            # Обычная фильтрация
            filters = {}
            if well_id:
                filters["well_id"] = well_id
            if fluid_id:
                filters["fluid_id"] = fluid_id
            if field_id:
                filters["field_id"] = field_id
            if development_object_id:
                filters["development_object_id"] = development_object_id
            if fluid_type:
                filters["fluid_type"] = fluid_type
            
            records, total = await production_service.get_multi(
                db, 
                limit=limit, 
                offset=offset, 
                filters=filters
            )
        
        return PaginatedResponse(
            data=[ProductionResponseSchema.model_validate(record) for record in records],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error getting production records: {str(e)}")
        raise internal_server_exception()


@router.get(
    "/{record_id}",
    response_model=ProductionResponseSchema,
    summary="Получить запись добычи по ID"
)
async def get_production_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
) -> ProductionResponseSchema:
    """Получение записи добычи по ID"""
    try:
        record = await production_service.get_by_id_or_404(db, record_id)
        return ProductionResponseSchema.model_validate(record)
    except NotFoundError:
        raise not_found_exception("Production record not found")
    except Exception as e:
        logger.error(f"Error getting production record {record_id}: {str(e)}")
        raise internal_server_exception()


@router.patch(
    "/{record_id}",
    response_model=ProductionResponseSchema,
    summary="Обновить запись добычи"
)
async def update_production_record(
    record_id: int,
    production_data: ProductionUpdateSchema,
    db: AsyncSession = Depends(get_db)
) -> ProductionResponseSchema:
    """Частичное обновление записи добычи"""
    try:
        update_data = production_data.model_dump(exclude_unset=True)
        if not update_data:
            raise validation_exception("No data provided for update")
        
        record = await production_service.update(db, record_id, update_data)
        return ProductionResponseSchema.model_validate(record)
    except NotFoundError:
        raise not_found_exception("Production record not found")
    except ValidationError as e:
        raise validation_exception(str(e))
    except Exception as e:
        logger.error(f"Error updating production record {record_id}: {str(e)}")
        raise internal_server_exception()


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить запись добычи"
)
async def delete_production_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление записи добычи"""
    try:
        await production_service.delete(db, record_id)
    except NotFoundError:
        raise not_found_exception("Production record not found")
    except Exception as e:
        logger.error(f"Error deleting production record {record_id}: {str(e)}")
        raise internal_server_exception()


@router.post(
    "/bulk",
    response_model=BulkCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Массовое создание записей добычи"
)
async def bulk_create_production_records(
    records_data: List[ProductionCreateSchema],
    db: AsyncSession = Depends(get_db)
) -> BulkCreateResponse:
    """Массовое создание записей добычи - все или никакие"""
    start_time = time.time()
    
    try:
        records_data_dict = [record.model_dump() for record in records_data]
        created_records = await production_service.bulk_create(db, records_data_dict)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return BulkCreateResponse(
            created=len(created_records),
            total=len(records_data),
            ids=[record.id for record in created_records],
            processing_time_ms=processing_time
        )
        
    except ValidationError as e:
        logger.warning(f"Bulk create validation failed: {str(e)}")
        raise validation_exception(str(e), e.details)
    except Exception as e:
        logger.error(f"Error in bulk create production records: {str(e)}")
        raise internal_server_exception()

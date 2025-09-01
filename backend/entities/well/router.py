"""
FastAPI роутер для скважин
"""
import time
from typing import List
from fastapi import APIRouter, Depends, status

from backend.core.logging import get_logger
from backend.shared.dependencies import get_db
from backend.shared.base_schema import PaginatedResponse, BulkCreateResponse
from backend.entities.well.service import well_service
from backend.entities.well.schema import (
    WellCreateSchema,
    WellUpdateSchema,
    WellResponseSchema
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

router = APIRouter(prefix="/wells", tags=["wells"])


@router.post(
    "/",
    response_model=WellResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую скважину"
)
async def create_well(
    well_data: WellCreateSchema,
    db: AsyncSession = Depends(get_db)
) -> WellResponseSchema:
    """Создание новой скважины"""
    try:
        well = await well_service.create(db, well_data.model_dump())
        return WellResponseSchema.model_validate(well)
    except ValidationError as e:
        raise validation_exception(str(e))
    except Exception as e:
        logger.error(f"Error creating well: {str(e)}")
        raise internal_server_exception()


@router.get(
    "/",
    response_model=PaginatedResponse[WellResponseSchema],
    summary="Получить список скважин"
)
async def get_wells(
    field_id: int = None,
    fluid_type: FluidTypeEnum = None,
    name: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[WellResponseSchema]:
    """Получение списка скважин с фильтрацией и пагинацией"""
    try:
        filters = {}
        if field_id:
            filters["field_id"] = field_id
        if fluid_type:
            filters["fluid_type"] = fluid_type
        if name:
            filters["name"] = name
        
        wells, total = await well_service.get_multi(
            db, 
            limit=limit, 
            offset=offset, 
            filters=filters
        )
        
        return PaginatedResponse(
            data=[WellResponseSchema.model_validate(well) for well in wells],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error getting wells: {str(e)}")
        raise internal_server_exception()


@router.get(
    "/{well_id}",
    response_model=WellResponseSchema,
    summary="Получить скважину по ID"
)
async def get_well(
    well_id: int,
    db: AsyncSession = Depends(get_db)
) -> WellResponseSchema:
    """Получение скважины по ID"""
    try:
        well = await well_service.get_by_id_or_404(db, well_id)
        return WellResponseSchema.model_validate(well)
    except NotFoundError:
        raise not_found_exception("Well not found")
    except Exception as e:
        logger.error(f"Error getting well {well_id}: {str(e)}")
        raise internal_server_exception()


@router.patch(
    "/{well_id}",
    response_model=WellResponseSchema,
    summary="Обновить скважину"
)
async def update_well(
    well_id: int,
    well_data: WellUpdateSchema,
    db: AsyncSession = Depends(get_db)
) -> WellResponseSchema:
    """Частичное обновление скважины"""
    try:
        update_data = well_data.model_dump(exclude_unset=True)
        if not update_data:
            raise validation_exception("No data provided for update")
        
        well = await well_service.update(db, well_id, update_data)
        return WellResponseSchema.model_validate(well)
    except NotFoundError:
        raise not_found_exception("Well not found")
    except ValidationError as e:
        raise validation_exception(str(e))
    except Exception as e:
        logger.error(f"Error updating well {well_id}: {str(e)}")
        raise internal_server_exception()


@router.delete(
    "/{well_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить скважину"
)
async def delete_well(
    well_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление скважины"""
    try:
        await well_service.delete(db, well_id)
    except NotFoundError:
        raise not_found_exception("Well not found")
    except Exception as e:
        logger.error(f"Error deleting well {well_id}: {str(e)}")
        raise internal_server_exception()


@router.post(
    "/bulk",
    response_model=BulkCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Массовое создание скважин"
)
async def bulk_create_wells(
    wells_data: List[WellCreateSchema],
    db: AsyncSession = Depends(get_db)
) -> BulkCreateResponse:
    """Массовое создание скважин - все или никакие"""
    start_time = time.time()
    
    try:
        wells_data_dict = [well.model_dump() for well in wells_data]
        created_wells = await well_service.bulk_create(db, wells_data_dict)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return BulkCreateResponse(
            created=len(created_wells),
            total=len(wells_data),
            ids=[well.id for well in created_wells],
            processing_time_ms=processing_time
        )
        
    except ValidationError as e:
        logger.warning(f"Bulk create validation failed: {str(e)}")
        raise validation_exception(str(e), e.details)
    except Exception as e:
        logger.error(f"Error in bulk create wells: {str(e)}")
        raise internal_server_exception()

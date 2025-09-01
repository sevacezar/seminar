"""
FastAPI роутер для флюидов
"""
import time
from typing import List
from fastapi import APIRouter, Depends, status

from backend.core.logging import get_logger
from backend.shared.dependencies import get_db
from backend.shared.base_schema import PaginatedResponse, BulkCreateResponse
from backend.entities.fluid.service import fluid_service
from backend.entities.fluid.schema import (
    FluidCreateSchema,
    FluidUpdateSchema,
    FluidResponseSchema
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

router = APIRouter(prefix="/fluids", tags=["fluids"])


@router.post(
    "/",
    response_model=FluidResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый флюид"
)
async def create_fluid(
    fluid_data: FluidCreateSchema,
    db: AsyncSession = Depends(get_db)
) -> FluidResponseSchema:
    """Создание нового флюида"""
    try:
        fluid = await fluid_service.create(db, fluid_data.model_dump())
        return FluidResponseSchema.model_validate(fluid)
    except ValidationError as e:
        raise validation_exception(str(e))
    except Exception as e:
        logger.error(f"Error creating fluid: {str(e)}")
        raise internal_server_exception()


@router.get(
    "/",
    response_model=PaginatedResponse[FluidResponseSchema],
    summary="Получить список флюидов"
)
async def get_fluids(
    fluid_type: FluidTypeEnum = None,
    development_object_id: int = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[FluidResponseSchema]:
    """Получение списка флюидов с фильтрацией и пагинацией"""
    try:
        filters = {}
        if fluid_type:
            filters["fluid_type"] = fluid_type
        if development_object_id:
            filters["development_object_id"] = development_object_id
        
        fluids, total = await fluid_service.get_multi(
            db, 
            limit=limit, 
            offset=offset, 
            filters=filters
        )
        
        return PaginatedResponse(
            data=[FluidResponseSchema.model_validate(fluid) for fluid in fluids],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error getting fluids: {str(e)}")
        raise internal_server_exception()


@router.get(
    "/{fluid_id}",
    response_model=FluidResponseSchema,
    summary="Получить флюид по ID"
)
async def get_fluid(
    fluid_id: int,
    db: AsyncSession = Depends(get_db)
) -> FluidResponseSchema:
    """Получение флюида по ID"""
    try:
        fluid = await fluid_service.get_by_id_or_404(db, fluid_id)
        return FluidResponseSchema.model_validate(fluid)
    except NotFoundError:
        raise not_found_exception("Fluid not found")
    except Exception as e:
        logger.error(f"Error getting fluid {fluid_id}: {str(e)}")
        raise internal_server_exception()


@router.patch(
    "/{fluid_id}",
    response_model=FluidResponseSchema,
    summary="Обновить флюид"
)
async def update_fluid(
    fluid_id: int,
    fluid_data: FluidUpdateSchema,
    db: AsyncSession = Depends(get_db)
) -> FluidResponseSchema:
    """Частичное обновление флюида"""
    try:
        update_data = fluid_data.model_dump(exclude_unset=True)
        if not update_data:
            raise validation_exception("No data provided for update")
        
        fluid = await fluid_service.update(db, fluid_id, update_data)
        return FluidResponseSchema.model_validate(fluid)
    except NotFoundError:
        raise not_found_exception("Fluid not found")
    except ValidationError as e:
        raise validation_exception(str(e))
    except Exception as e:
        logger.error(f"Error updating fluid {fluid_id}: {str(e)}")
        raise internal_server_exception()


@router.delete(
    "/{fluid_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить флюид"
)
async def delete_fluid(
    fluid_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление флюида"""
    try:
        await fluid_service.delete(db, fluid_id)
    except NotFoundError:
        raise not_found_exception("Fluid not found")
    except Exception as e:
        logger.error(f"Error deleting fluid {fluid_id}: {str(e)}")
        raise internal_server_exception()


@router.post(
    "/bulk",
    response_model=BulkCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Массовое создание флюидов"
)
async def bulk_create_fluids(
    fluids_data: List[FluidCreateSchema],
    db: AsyncSession = Depends(get_db)
) -> BulkCreateResponse:
    """Массовое создание флюидов - все или никакие"""
    start_time = time.time()
    
    try:
        fluids_data_dict = [fluid.model_dump() for fluid in fluids_data]
        created_fluids = await fluid_service.bulk_create(db, fluids_data_dict)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return BulkCreateResponse(
            created=len(created_fluids),
            total=len(fluids_data),
            ids=[fluid.id for fluid in created_fluids],
            processing_time_ms=processing_time
        )
        
    except ValidationError as e:
        logger.warning(f"Bulk create validation failed: {str(e)}")
        raise validation_exception(str(e), e.details)
    except Exception as e:
        logger.error(f"Error in bulk create fluids: {str(e)}")
        raise internal_server_exception()

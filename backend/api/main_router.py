"""
Главный роутер API, объединяющий все роутеры сущностей
"""
from fastapi import APIRouter

from backend.entities.field.router import router as field_router
from backend.entities.development_object.router import router as development_object_router
from backend.entities.well.router import router as well_router
from backend.entities.fluid.router import router as fluid_router
from backend.entities.production.router import router as production_router
from backend.entities.analytics.router import router as analytics_router
from backend.entities.enums_info.router import router as enums_router

# Создание главного роутера
api_router = APIRouter()

# Подключение роутеров сущностей
api_router.include_router(field_router)
api_router.include_router(development_object_router)
api_router.include_router(well_router)
api_router.include_router(fluid_router)
api_router.include_router(production_router)

# Подключение роутера аналитики
api_router.include_router(analytics_router)

# Подключение роутера для enum'ов
api_router.include_router(enums_router)

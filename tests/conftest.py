"""
Конфигурация pytest для тестов
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest_asyncio
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from main import app
from backend.core.database import get_db
from backend.core.base import Base
from backend.core.config import settings


# Тестовая база данных
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

# Создание тестового движка
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

# Создание фабрики сессий для тестов
TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Создание event loop для всей сессии тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_test_db():
    """Создание тестовой базы данных и таблиц"""
    # Создание тестовой БД
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        isolation_level="AUTOCOMMIT"
    )
    
    async with engine.begin() as conn:
        # Удаляем тестовую БД если существует
        await conn.execute(text("DROP DATABASE IF EXISTS test"))
        # Создаем тестовую БД
        await conn.execute(text("CREATE DATABASE test"))
    
    await engine.dispose()
    
    # Создание таблиц в тестовой БД
    async with test_engine.begin() as conn:
        # Импортируем все модели для создания таблиц
        import backend.core.models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Очистка после всех тестов
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(setup_test_db):
    """Создание сессии БД для каждого теста"""
    async with TestAsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """Создание HTTP клиента для тестов"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    # Очистка переопределения зависимостей
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_data(db_session):
    """Создание тестовых данных"""
    from backend.entities.field.model import Field
    from backend.entities.development_object.model import DevelopmentObject
    from backend.entities.well.model import Well
    from backend.entities.fluid.model import Fluid
    from backend.entities.production.model import Production
    from backend.shared.enums import SedimentComplexEnum, FluidTypeEnum
    from datetime import date
    from decimal import Decimal
    
    # Создаем месторождения
    field1 = Field(name="Месторождение А", operator="Газпром")
    field2 = Field(name="Месторождение Б", operator="Роснефть")
    
    db_session.add_all([field1, field2])
    await db_session.flush()  # Получаем ID
    
    # Создаем объекты разработки
    dev_obj1 = DevelopmentObject(
        name="Объект А1", 
        field_id=field1.id, 
        sediment_complex=SedimentComplexEnum.SENOMAN
    )
    dev_obj2 = DevelopmentObject(
        name="Объект Б1", 
        field_id=field2.id, 
        sediment_complex=SedimentComplexEnum.TURON
    )
    
    db_session.add_all([dev_obj1, dev_obj2])
    await db_session.flush()
    
    # Создаем флюиды
    # Сеноман и турон - только газ
    fluid1 = Fluid(fluid_type=FluidTypeEnum.GAS, development_object_id=dev_obj1.id)
    fluid2 = Fluid(fluid_type=FluidTypeEnum.GAS, development_object_id=dev_obj2.id)
    
    db_session.add_all([fluid1, fluid2])
    await db_session.flush()
    
    # Создаем скважины
    well1 = Well(name="Скважина А-1", field_id=field1.id, fluid_type=FluidTypeEnum.GAS)
    well2 = Well(name="Скважина Б-1", field_id=field2.id, fluid_type=FluidTypeEnum.GAS)
    
    db_session.add_all([well1, well2])
    await db_session.flush()
    
    # Создаем данные добычи за 3 года по месяцам
    production_records = []
    
    for year in [2021, 2022, 2023]:
        for month in range(1, 13):
            # Добыча для месторождения А
            production_records.append(Production(
                well_id=well1.id,
                fluid_id=fluid1.id,
                date=date(year, month, 1),
                amount=Decimal("1000.0") + Decimal(str(month * 10)),  # Вариация по месяцам
                unit="тыс. м³",
                fluid_type=FluidTypeEnum.GAS,
                field_id=field1.id,
                development_object_id=dev_obj1.id
            ))
            
            # Добыча для месторождения Б
            production_records.append(Production(
                well_id=well2.id,
                fluid_id=fluid2.id,
                date=date(year, month, 1),
                amount=Decimal("800.0") + Decimal(str(month * 8)),  # Другие значения
                unit="тыс. м³",
                fluid_type=FluidTypeEnum.GAS,
                field_id=field2.id,
                development_object_id=dev_obj2.id
            ))
    
    db_session.add_all(production_records)
    await db_session.commit()
    
    # Возвращаем созданные объекты для использования в тестах
    yield {
        "fields": [field1, field2],
        "dev_objects": [dev_obj1, dev_obj2],
        "wells": [well1, well2],
        "fluids": [fluid1, fluid2],
        "production_count": len(production_records)
    }
    
    # Очистка данных после теста
    await db_session.execute(text("TRUNCATE TABLE production RESTART IDENTITY CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE wells RESTART IDENTITY CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE fluids RESTART IDENTITY CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE development_objects RESTART IDENTITY CASCADE"))
    await db_session.execute(text("TRUNCATE TABLE fields RESTART IDENTITY CASCADE"))
    await db_session.commit()

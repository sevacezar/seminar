"""
Прямой тест SQLAlchemy без FastAPI
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from backend.entities.analytics.service import analytics_service
from backend.shared.enums import FluidTypeEnum, AggregationStepEnum
from datetime import date

# Тестовая база данных
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def direct_test():
    """Прямой тест аналитического сервиса"""
    print("🔍 Прямой тест аналитического сервиса")
    
    async with TestAsyncSessionLocal() as db_session:
        # Проверяем данные в БД
        result = await db_session.execute(text("SELECT COUNT(*) FROM production"))
        count = result.scalar()
        print(f"📊 Записей в production: {count}")
        
        if count > 0:
            # Проверяем типы флюидов
            result = await db_session.execute(text("SELECT DISTINCT fluid_type FROM production"))
            fluid_types = result.scalars().all()
            print(f"🧪 Типы флюидов в БД: {list(fluid_types)}")
            
            # Проверяем значения enum'ов
            print(f"🏷️  FluidTypeEnum.GAS = {FluidTypeEnum.GAS}")
            print(f"🏷️  FluidTypeEnum.GAS.value = '{FluidTypeEnum.GAS.value}'")
            print(f"🏷️  AggregationStepEnum.YEARLY = {AggregationStepEnum.YEARLY}")
            print(f"🏷️  AggregationStepEnum.YEARLY.value = '{AggregationStepEnum.YEARLY.value}'")
            
            # Тестируем аналитический сервис напрямую
            print("\n🧪 Тестируем аналитический сервис...")
            try:
                result = await analytics_service.get_production_dynamics(
                    db=db_session,
                    date_from=date(2021, 1, 1),
                    date_to=date(2023, 12, 31),
                    fluid_type=FluidTypeEnum.GAS,
                    aggregation_step=AggregationStepEnum.YEARLY
                )
                
                print("✅ Аналитический сервис работает!")
                print(f"📊 Найдено месторождений: {result.metadata.response.total_fields}")
                print(f"📅 Периодов: {result.metadata.response.total_periods}")
                print(f"📈 Отчетные даты: {result.reporting_dates}")
                
                for field in result.fields:
                    print(f"🏭 {field.field_name}: {field.production_by_period}")
                
            except Exception as e:
                print(f"❌ Ошибка в аналитическом сервисе: {e}")
        else:
            print("❌ Нет данных для тестирования")
    
    await test_engine.dispose()


if __name__ == "__main__":
    asyncio.run(direct_test())

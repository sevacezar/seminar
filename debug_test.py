"""
Отладочный тест для проверки данных в БД
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text, select

from backend.entities.production.model import Production
from backend.shared.enums import FluidTypeEnum

# Тестовая база данных
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestAsyncSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def debug_data():
    """Отладка данных в БД"""
    print("🔍 Проверяем данные в БД")
    
    async with TestAsyncSessionLocal() as db_session:
        # Проверяем что есть в таблице production
        result = await db_session.execute(text("SELECT COUNT(*) FROM production"))
        count = result.scalar()
        print(f"📊 Записей в production: {count}")
        
        if count > 0:
            # Проверяем типы флюидов
            result = await db_session.execute(text("SELECT DISTINCT fluid_type FROM production"))
            fluid_types = result.scalars().all()
            print(f"🧪 Типы флюидов в БД: {list(fluid_types)}")
            
            # Проверяем enum значения
            print(f"🏷️  FluidTypeEnum.GAS.value = '{FluidTypeEnum.GAS.value}'")
            print(f"🏷️  FluidTypeEnum.GAS = {FluidTypeEnum.GAS}")
            
            # Пробуем запрос с разными значениями
            for test_value in ['газ', 'GAS', FluidTypeEnum.GAS.value, FluidTypeEnum.GAS]:
                try:
                    query = select(Production).where(Production.fluid_type == test_value).limit(1)
                    result = await db_session.execute(query)
                    record = result.scalar_one_or_none()
                    print(f"✅ Запрос с '{test_value}' ({type(test_value)}): {'найдена запись' if record else 'не найдено'}")
                except Exception as e:
                    print(f"❌ Запрос с '{test_value}' ({type(test_value)}): ошибка - {e}")
    
    await test_engine.dispose()


if __name__ == "__main__":
    asyncio.run(debug_data())

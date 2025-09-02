#!/usr/bin/env python3
"""
Скрипт для очистки всех данных из базы данных
"""

import asyncio
import sys
import os

# Добавляем корневую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import AsyncSessionLocal
from backend.entities.production.model import Production
from backend.entities.well.model import Well
from backend.entities.development_object.model import DevelopmentObject
from backend.entities.field.model import Field
from backend.entities.fluid.model import Fluid
from sqlalchemy import delete


async def clear_database():
    """Очищает все данные из базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            print("🗑️  Начинаем очистку базы данных...")
            
            # Удаляем данные в правильном порядке (с учетом внешних ключей)
            print("  - Удаляем данные о добыче...")
            await session.execute(delete(Production))
            
            print("  - Удаляем данные о скважинах...")
            await session.execute(delete(Well))
            
            print("  - Удаляем данные о флюидах...")
            await session.execute(delete(Fluid))
            
            print("  - Удаляем данные об объектах разработки...")
            await session.execute(delete(DevelopmentObject))
            
            print("  - Удаляем данные о месторождениях...")
            await session.execute(delete(Field))
            
            # Подтверждаем изменения
            await session.commit()
            
            print("✅ База данных успешно очищена!")
            
        except Exception as e:
            print(f"❌ Ошибка при очистке базы данных: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(clear_database())

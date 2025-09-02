#!/usr/bin/env python3
"""
Простой тест для эндпойнта добавления месторождения
Пример для обучения студентов тестированию API

Этот тест:
1. Создает новое месторождение через API
2. Проверяет, что ответ содержит правильные данные
3. Проверяет, что месторождение создалось в БД
4. Удаляет созданное месторождение
"""

import pytest
import httpx
import asyncio
import sys
import os

# Добавляем корневую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import AsyncSessionLocal
from backend.entities.field.model import Field
from backend.entities.development_object.model import DevelopmentObject
from backend.entities.well.model import Well
from backend.entities.fluid.model import Fluid
from backend.entities.production.model import Production
from sqlalchemy import select


# Конфигурация API
API_BASE_URL = "http://localhost:8000/api/v1"


class TestFieldEndpoint:
    """Тест для эндпойнта работы с месторождениями"""
    
    @pytest.mark.asyncio
    async def test_create_and_delete_field(self):
        """
        Тест создания и удаления месторождения
        
        Этот тест демонстрирует:
        - Создание ресурса через API
        - Проверку ответа API
        - Проверку сохранения в БД
        - Очистку после теста
        """
        
        # Данные для создания месторождения
        field_data = {
            "name": "Тестовое месторождение",
            "operator": "Тестовый оператор"
        }
        
        created_field_id = None
        
        try:
            # 1. Создаем месторождение через API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE_URL}/fields/",
                    json=field_data
                )
            
            # 2. Проверяем, что запрос прошел успешно
            assert response.status_code == 201, f"Ожидался код 201, получен {response.status_code}"
            
            # 3. Проверяем структуру ответа
            response_data = response.json()
            assert "id" in response_data, "В ответе должен быть ID"
            assert "name" in response_data, "В ответе должно быть название"
            assert "operator" in response_data, "В ответе должен быть оператор"
            
            # 4. Проверяем, что данные в ответе соответствуют отправленным
            assert response_data["name"] == field_data["name"], "Название не совпадает"
            assert response_data["operator"] == field_data["operator"], "Оператор не совпадает"
            
            created_field_id = response_data["id"]
            print(f"✅ Месторождение создано с ID: {created_field_id}")
            
            # 5. Проверяем, что месторождение сохранилось в БД
            async with AsyncSessionLocal() as session:
                # Ищем созданное месторождение в БД
                result = await session.execute(
                    select(Field).where(Field.id == created_field_id)
                )
                db_field = result.scalar_one_or_none()
                
                # Проверяем, что месторождение найдено в БД
                assert db_field is not None, "Месторождение не найдено в БД"
                assert db_field.name == field_data["name"], "Название в БД не совпадает"
                assert db_field.operator == field_data["operator"], "Оператор в БД не совпадает"
                
                print(f"✅ Месторождение найдено в БД: {db_field.name}")
            
            # 6. Проверяем, что можем получить месторождение через GET API
            async with httpx.AsyncClient() as client:
                get_response = await client.get(f"{API_BASE_URL}/fields/{created_field_id}")
            
            assert get_response.status_code == 200, "Не удалось получить созданное месторождение"
            get_data = get_response.json()
            assert get_data["name"] == field_data["name"], "Данные при получении не совпадают"
            
            print(f"✅ Месторождение успешно получено через GET API")
            
        finally:
            # 7. Очищаем: удаляем созданное месторождение
            if created_field_id:
                async with httpx.AsyncClient() as client:
                    delete_response = await client.delete(f"{API_BASE_URL}/fields/{created_field_id}")
                
                # Проверяем, что удаление прошло успешно (204 = No Content)
                assert delete_response.status_code in [200, 204], f"Не удалось удалить месторождение: {delete_response.status_code}"
                
                # Проверяем, что месторождение действительно удалено из БД
                async with AsyncSessionLocal() as session:
                    result = await session.execute(
                        select(Field).where(Field.id == created_field_id)
                    )
                    db_field = result.scalar_one_or_none()
                    assert db_field is None, "Месторождение не было удалено из БД"
                
                print(f"✅ Месторождение успешно удалено")
        
        print("🎉 Все тесты прошли успешно!")


# Функция для запуска теста без pytest (для простоты)
async def run_test():
    """Запуск теста без pytest"""
    test_instance = TestFieldEndpoint()
    await test_instance.test_create_and_delete_field()


if __name__ == "__main__":
    print("🧪 Запуск простого теста для эндпойнта месторождений")
    print("=" * 60)
    print("Убедитесь, что:")
    print("1. Backend API запущен на http://localhost:8000")
    print("2. База данных PostgreSQL запущена")
    print("=" * 60)
    
    try:
        asyncio.run(run_test())
    except Exception as e:
        print(f"❌ Тест не прошел: {e}")
        sys.exit(1)

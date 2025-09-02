#!/usr/bin/env python3
"""
Скрипт для проверки работоспособности API перед наполнением данными
"""

import asyncio
import aiohttp
import json

API_BASE_URL = "http://localhost:8000/api/v1"


async def test_api_endpoints():
    """Тестирование основных API endpoints"""
    print("🧪 Тестирование API endpoints...")
    
    async with aiohttp.ClientSession() as session:
        # Тестируем health check
        try:
            async with session.get(f"{API_BASE_URL.replace('/v1', '')}/health") as response:
                if response.status == 200:
                    print("✅ Health check: OK")
                else:
                    print(f"❌ Health check: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
        
        # Тестируем enums
        endpoints_to_test = [
            ("/enums/fluid-types", "Типы флюидов"),
            ("/enums/sediment-complexes", "Комплексы отложений"),
            ("/enums/aggregation-steps", "Шаги агрегации"),
            ("/fields?limit=1", "Месторождения")
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                async with session.get(f"{API_BASE_URL}{endpoint}") as response:
                    if response.status in [200, 404]:  # 404 для пустых данных - это норма
                        data = await response.json()
                        print(f"✅ {description}: OK (статус {response.status})")
                    else:
                        print(f"❌ {description}: {response.status}")
                        return False
            except Exception as e:
                print(f"❌ {description} failed: {e}")
                return False
        
        print("🎉 Все API endpoints работают корректно!")
        return True


async def main():
    """Главная функция"""
    print("🔧 Тестирование API перед наполнением данными")
    print("=" * 50)
    
    success = await test_api_endpoints()
    
    if success:
        print("\n✅ API готов к наполнению данными!")
        print("Запустите: python scripts/populate_database.py")
    else:
        print("\n❌ API не готов. Проверьте что backend запущен:")
        print("   cd backend && uvicorn main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())

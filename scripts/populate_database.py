#!/usr/bin/env python3
"""
Скрипт для наполнения базы данных тестовыми данными через API
"""

import asyncio
import aiohttp
import json
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import calendar

# Конфигурация API
API_BASE_URL = "http://localhost:8000/api/v1"

# Данные для генерации
OPERATORS = [
    "НефтеГазПром", 
    "СевернаяЭнерго", 
    "АрктикОйл", 
    "СибирьГаз", 
    "УралНефть"
]

FIELDS_DATA = [
    {"name": "Северное Сияние", "operator": "НефтеГазПром", "complexes": 4},
    {"name": "Белый Медведь", "operator": "НефтеГазПром", "complexes": 4},
    {"name": "Полярная Звезда", "operator": "СевернаяЭнерго", "complexes": 4},
    {"name": "Золотая Тундра", "operator": "АрктикОйл", "complexes": 3},
    {"name": "Синий Кит", "operator": "СевернаяЭнерго", "complexes": 3},
    {"name": "Морозное Утро", "operator": "СибирьГаз", "complexes": 2},
    {"name": "Снежный Барс", "operator": "УралНефть", "complexes": 2},
    {"name": "Ледяной Дракон", "operator": "АрктикОйл", "complexes": 2},
    {"name": "Северный Ветер", "operator": "СибирьГаз", "complexes": 1},
    {"name": "Кристальное", "operator": "УралНефть", "complexes": 1}
]

COMPLEXES = ["турон", "сеноман", "неоком", "ачимовка"]
FLUID_TYPES = ["газ", "нефть", "конденсат"]

# Дебиты скважин (в сутки)
GAS_DEBIT_RANGE = (50000, 800000)  # м3/сут
OIL_DEBIT_RANGE = (20, 100)  # т/сут
CONDENSATE_RATIO_RANGE = (50, 150)  # г/м3


class DatabasePopulator:
    def __init__(self):
        self.session = None
        self.created_data = {
            'fields': [],
            'development_objects': [],
            'wells': [],
            'fluids': [],
            'production': []
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Any = None) -> Dict:
        """Выполнение HTTP запроса к API"""
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(url, params=data) as response:
                    result = await response.json()
                    if response.status >= 400:
                        print(f"❌ Ошибка GET {url}: {response.status} - {result}")
                        return {}
                    return result
            
            elif method.upper() == 'POST':
                headers = {'Content-Type': 'application/json'}
                async with self.session.post(url, json=data, headers=headers) as response:
                    result = await response.json()
                    if response.status >= 400:
                        print(f"❌ Ошибка POST {url}: {response.status} - {result}")
                        return {}
                    return result
                    
        except Exception as e:
            print(f"❌ Исключение при запросе {method} {url}: {e}")
            return {}
    
    async def create_fields(self) -> List[Dict]:
        """Создание месторождений"""
        print("🏭 Создание месторождений...")
        
        fields = []
        for field_data in FIELDS_DATA:
            field = {
                "name": field_data["name"],
                "operator": field_data["operator"]
            }
            
            result = await self.make_request('POST', '/fields', field)
            if result:
                fields.append(result)
                print(f"  ✅ Создано месторождение: {field['name']}")
            else:
                print(f"  ❌ Ошибка создания месторождения: {field['name']}")
        
        self.created_data['fields'] = fields
        return fields
    
    async def create_development_objects(self, fields: List[Dict]) -> List[Dict]:
        """Создание объектов разработки (комплексы отложений)"""
        print("🗻 Создание объектов разработки...")
        
        dev_objects = []
        
        for i, field in enumerate(fields):
            field_config = FIELDS_DATA[i]
            complexes_count = field_config["complexes"]
            
            # Выбираем комплексы для этого месторождения
            field_complexes = COMPLEXES[:complexes_count]
            
            for complex_name in field_complexes:
                dev_obj = {
                    "name": f"{field['name']} - {complex_name.capitalize()}",
                    "field_id": field["id"],
                    "sediment_complex": complex_name
                }
                
                result = await self.make_request('POST', '/development-objects', dev_obj)
                if result:
                    dev_objects.append(result)
                    print(f"  ✅ Создан объект: {dev_obj['name']}")
        
        self.created_data['development_objects'] = dev_objects
        return dev_objects
    
    async def create_wells(self, fields: List[Dict]) -> List[Dict]:
        """Создание скважин"""
        print("🔧 Создание скважин...")
        
        wells = []
        
        for field in fields:
            wells_count = random.randint(10, 50)
            
            for i in range(wells_count):
                # Определяем тип флюида для скважины
                fluid_type = random.choice(FLUID_TYPES)
                
                well = {
                    "name": f"{field['name']}-{i+1:03d}",
                    "field_id": field["id"],
                    "fluid_type": fluid_type
                }
                
                result = await self.make_request('POST', '/wells', well)
                if result:
                    wells.append(result)
            
            print(f"  ✅ Создано {wells_count} скважин для {field['name']}")
        
        self.created_data['wells'] = wells
        return wells
    
    async def create_fluids(self, dev_objects: List[Dict]) -> List[Dict]:
        """Создание флюидов для объектов разработки"""
        print("⛽ Создание флюидов...")
        
        fluids = []
        
        for dev_obj in dev_objects:
            complex_name = dev_obj["sediment_complex"]
            
            # Определяем какие флюиды есть в каждом комплексе
            if complex_name in ["неоком", "ачимовка"]:
                # В неокоме и ачимовке могут быть все три типа
                fluid_types = FLUID_TYPES
            else:
                # В других комплексах только газ
                fluid_types = ["газ"]
            
            for fluid_type in fluid_types:
                fluid = {
                    "fluid_type": fluid_type,
                    "development_object_id": dev_obj["id"]
                }
                
                result = await self.make_request('POST', '/fluids', fluid)
                if result:
                    fluids.append(result)
        
        print(f"  ✅ Создано {len(fluids)} флюидов")
        self.created_data['fluids'] = fluids
        return fluids
    
    def calculate_monthly_production(self, well: Dict, fluid: Dict, days_in_month: int, 
                                   year: int, base_year: int = 2015) -> float:
        """Расчет месячной добычи для скважины с учетом истощения"""
        fluid_type = fluid["fluid_type"]
        
        # Коэффициент истощения по годам (каждый год дебит снижается на 3-7%)
        years_passed = year - base_year
        depletion_factor = (0.97 ** years_passed) * random.uniform(0.95, 1.05)  # +- 5% случайности
        
        if fluid_type == "газ":
            base_daily_debit = random.randint(*GAS_DEBIT_RANGE)  # м3/сут
            daily_debit = base_daily_debit * depletion_factor
            return daily_debit * days_in_month  # м3/месяц
        
        elif fluid_type == "нефть":
            base_daily_debit = random.randint(*OIL_DEBIT_RANGE)  # т/сут
            daily_debit = base_daily_debit * depletion_factor
            return daily_debit * days_in_month  # т/месяц
        
        elif fluid_type == "конденсат":
            # Конденсат считается от газа
            base_gas_daily = random.randint(*GAS_DEBIT_RANGE)  # м3/сут газа
            gas_daily = base_gas_daily * depletion_factor
            condensate_ratio = random.randint(*CONDENSATE_RATIO_RANGE)  # г/м3
            daily_condensate = (gas_daily * condensate_ratio) / 1000  # кг/сут
            return (daily_condensate * days_in_month) / 1000  # т/месяц
        
        return 0
    
    async def create_production_data(self, wells: List[Dict], fluids: List[Dict], 
                                   dev_objects: List[Dict]) -> List[Dict]:
        """Создание данных о добыче"""
        print("📊 Создание данных о добыче...")
        
        production_records = []
        
        # Создаем данные за 10 лет (с января 2015 по декабрь 2024)
        start_date = date(2015, 1, 1)
        
        # Группируем флюиды по объектам разработки
        fluids_by_dev_obj = {}
        for fluid in fluids:
            dev_obj_id = fluid["development_object_id"]
            if dev_obj_id not in fluids_by_dev_obj:
                fluids_by_dev_obj[dev_obj_id] = []
            fluids_by_dev_obj[dev_obj_id].append(fluid)
        
        # Группируем объекты разработки по месторождениям
        dev_objs_by_field = {}
        for dev_obj in dev_objects:
            field_id = dev_obj["field_id"]
            if field_id not in dev_objs_by_field:
                dev_objs_by_field[field_id] = []
            dev_objs_by_field[field_id].append(dev_obj)
        
        for month in range(120):  # 120 месяцев (10 лет)
            # Вычисляем текущую дату
            year = start_date.year + (month // 12)
            month_in_year = (month % 12) + 1
            current_date = date(year, month_in_year, 1)
            
            # Дата записи - первое число следующего месяца
            if month_in_year == 12:
                record_date = date(year + 1, 1, 1)
            else:
                record_date = date(year, month_in_year + 1, 1)
            
            days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
            
            print(f"  📅 Обрабатываем {current_date.strftime('%B %Y')}...")
            
            batch_records = []
            
            for well in wells:
                field_id = well["field_id"]
                well_fluid_type = well["fluid_type"]
                
                # Найдем подходящие объекты разработки и флюиды для этой скважины
                if field_id in dev_objs_by_field:
                    for dev_obj in dev_objs_by_field[field_id]:
                        dev_obj_id = dev_obj["id"]
                        
                        if dev_obj_id in fluids_by_dev_obj:
                            # Ищем флюид нужного типа для этого объекта
                            matching_fluids = [
                                f for f in fluids_by_dev_obj[dev_obj_id] 
                                if f["fluid_type"] == well_fluid_type
                            ]
                            
                            if matching_fluids:
                                fluid = matching_fluids[0]
                                
                                # Рассчитываем добычу с учетом истощения
                                amount = self.calculate_monthly_production(well, fluid, days_in_month, year)
                                
                                if amount > 0:
                                    unit = "тыс. м³" if fluid["fluid_type"] == "газ" else "т"
                                    
                                    # Для газа переводим в тысячи м³
                                    if fluid["fluid_type"] == "газ":
                                        amount = amount / 1000
                                    
                                    production = {
                                        "well_id": well["id"],
                                        "fluid_id": fluid["id"],
                                        "date": record_date.isoformat(),
                                        "amount": round(amount, 3),
                                        "unit": unit,
                                        "fluid_type": fluid["fluid_type"],
                                        "field_id": field_id,
                                        "development_object_id": dev_obj_id
                                    }
                                    
                                    batch_records.append(production)
            
            # Отправляем данные пачками по 100 записей
            for i in range(0, len(batch_records), 100):
                batch = batch_records[i:i+100]
                
                for record in batch:
                    result = await self.make_request('POST', '/production', record)
                    if result:
                        production_records.append(result)
            
            print(f"    ✅ Создано {len(batch_records)} записей за {current_date.strftime('%B %Y')}")
        
        self.created_data['production'] = production_records
        print(f"📊 Всего создано {len(production_records)} записей добычи")
        return production_records
    
    async def populate_database(self):
        """Основной метод наполнения базы данных"""
        print("🚀 Начинаем наполнение базы данных...")
        print("=" * 50)
        
        try:
            # 1. Создаем месторождения
            fields = await self.create_fields()
            if not fields:
                print("❌ Не удалось создать месторождения. Прерываем.")
                return
            
            # 2. Создаем объекты разработки
            dev_objects = await self.create_development_objects(fields)
            if not dev_objects:
                print("❌ Не удалось создать объекты разработки. Прерываем.")
                return
            
            # 3. Создаем скважины
            wells = await self.create_wells(fields)
            if not wells:
                print("❌ Не удалось создать скважины. Прерываем.")
                return
            
            # 4. Создаем флюиды
            fluids = await self.create_fluids(dev_objects)
            if not fluids:
                print("❌ Не удалось создать флюиды. Прерываем.")
                return
            
            # 5. Создаем данные о добыче
            production = await self.create_production_data(wells, fluids, dev_objects)
            
            print("=" * 50)
            print("🎉 Наполнение базы данных завершено!")
            print(f"📊 Создано:")
            print(f"  🏭 Месторождений: {len(fields)}")
            print(f"  🗻 Объектов разработки: {len(dev_objects)}")
            print(f"  🔧 Скважин: {len(wells)}")
            print(f"  ⛽ Флюидов: {len(fluids)}")
            print(f"  📈 Записей добычи: {len(production)}")
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            raise


async def main():
    """Главная функция"""
    print("🔧 Скрипт наполнения базы данных")
    print("Убедитесь, что backend API запущен на http://localhost:8000")
    print()
    
    # Проверяем доступность API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL.replace('/api/v1', '')}/health") as response:
                if response.status != 200:
                    print("❌ Backend API недоступен. Запустите сервер командой:")
                    print("   uvicorn main:app --reload")
                    return
                print("✅ Backend API доступен")
    except Exception as e:
        print(f"❌ Не удается подключиться к API: {e}")
        print("   Убедитесь, что backend запущен на http://localhost:8000")
        return
    
    # Запускаем наполнение
    async with DatabasePopulator() as populator:
        await populator.populate_database()


if __name__ == "__main__":
    asyncio.run(main())

"""
Тесты для аналитических операций
"""
import pytest
from httpx import AsyncClient
from datetime import date


class TestProductionDynamics:
    """Тесты для endpoint'а динамики добычи"""
    
    @pytest.mark.asyncio
    async def test_production_dynamics_yearly_aggregation(self, client: AsyncClient, test_data):
        """
        Тест агрегации добычи по годам для всех месторождений
        """
        # Подготовка данных запроса
        query_params = {
            "date_from": "2021-01-01",
            "date_to": "2023-12-31",
            "fluid_type": "газ",
            "aggregation_step": "год"
        }
        
        # Выполнение запроса
        response = await client.get("/api/v1/analytics/production/dynamics", params=query_params)
        
        # Проверка статуса ответа
        assert response.status_code == 200
        
        # Парсинг ответа
        data = response.json()
        
        # Проверка структуры ответа
        assert "metadata" in data
        assert "reporting_dates" in data
        assert "fields" in data
        assert "total" in data
        
        # Проверка метаданных
        metadata = data["metadata"]
        assert "request" in metadata
        assert "response" in metadata
        
        # Проверка параметров запроса в метаданных
        request_meta = metadata["request"]
        assert request_meta["date_from"] == "2021-01-01"
        assert request_meta["date_to"] == "2023-12-31"
        assert request_meta["fluid_type"] == "газ"
        assert request_meta["aggregation_step"] == "год"
        
        # Проверка метаданных ответа
        response_meta = metadata["response"]
        assert response_meta["total_fields"] == 2  # Два месторождения
        assert response_meta["total_periods"] == 3  # Три года (2021, 2022, 2023)
        assert response_meta["unit"] == "тыс. м³"  # Единица измерения для газа
        assert "generated_at" in response_meta
        
        # Проверка отчетных дат
        reporting_dates = data["reporting_dates"]
        assert len(reporting_dates) == 3
        assert "2021" in reporting_dates
        assert "2022" in reporting_dates
        assert "2023" in reporting_dates
        assert reporting_dates == ["2021", "2022", "2023"]  # Сортировка по возрастанию
        
        # Проверка данных по месторождениям
        fields = data["fields"]
        assert len(fields) == 2  # Два месторождения
        
        # Проверка структуры данных месторождения
        for field in fields:
            assert "field_id" in field
            assert "field_name" in field
            assert "production_by_period" in field
            assert len(field["production_by_period"]) == 3  # Три года
            
            # Проверка что все значения добычи положительные
            for production in field["production_by_period"]:
                assert production > 0
        
        # Проверка названий месторождений
        field_names = [f["field_name"] for f in fields]
        assert "Месторождение А" in field_names
        assert "Месторождение Б" in field_names
        
        # Проверка общих данных
        total = data["total"]
        assert "production_by_period" in total
        assert len(total["production_by_period"]) == 3  # Три года
        
        # Проверка что общая добыча равна сумме по месторождениям
        for i in range(3):
            expected_total = sum(field["production_by_period"][i] for field in fields)
            assert abs(total["production_by_period"][i] - expected_total) < 0.01
        
        # Проверка что общая добыча положительная
        for production in total["production_by_period"]:
            assert production > 0
        
        # Дополнительные проверки логики
        # Месторождение А должно иметь большую добычу (1000+ vs 800+)
        field_a = next(f for f in fields if f["field_name"] == "Месторождение А")
        field_b = next(f for f in fields if f["field_name"] == "Месторождение Б")
        
        # Проверяем что добыча месторождения А больше чем Б
        for i in range(3):
            assert field_a["production_by_period"][i] > field_b["production_by_period"][i]
    
    @pytest.mark.asyncio
    async def test_production_dynamics_with_field_filter(self, client: AsyncClient, test_data):
        """
        Тест агрегации добычи с фильтрацией по конкретному месторождению
        """
        # Получаем ID первого месторождения
        field_id = test_data["fields"][0].id
        
        query_params = {
            "date_from": "2021-01-01",
            "date_to": "2023-12-31",
            "fluid_type": "газ",
            "field_ids": [field_id],
            "aggregation_step": "год"
        }
        
        response = await client.get("/api/v1/analytics/production/dynamics", params=query_params)
        
        assert response.status_code == 200
        data = response.json()
        
        # Должно быть только одно месторождение
        assert len(data["fields"]) == 1
        assert data["metadata"]["response"]["total_fields"] == 1
        
        # Проверяем что это именно нужное месторождение
        field = data["fields"][0]
        assert field["field_id"] == field_id
        assert field["field_name"] == "Месторождение А"
    
    @pytest.mark.asyncio
    async def test_production_dynamics_with_sediment_filter(self, client: AsyncClient, test_data):
        """
        Тест агрегации добычи с фильтрацией по комплексу отложений
        """
        query_params = {
            "date_from": "2021-01-01",
            "date_to": "2023-12-31",
            "fluid_type": "газ",
            "sediment_complexes": ["сеноман"],  # Только сеноман
            "aggregation_step": "год"
        }
        
        response = await client.get("/api/v1/analytics/production/dynamics", params=query_params)
        
        assert response.status_code == 200
        data = response.json()
        
        # Должно быть только одно месторождение (с сеноманом)
        assert len(data["fields"]) == 1
        assert data["metadata"]["response"]["total_fields"] == 1
        
        # Проверяем что это месторождение А (у него сеноман)
        field = data["fields"][0]
        assert field["field_name"] == "Месторождение А"
    
    @pytest.mark.asyncio
    async def test_production_dynamics_monthly_aggregation(self, client: AsyncClient, test_data):
        """
        Тест агрегации добычи по месяцам за один год
        """
        query_params = {
            "date_from": "2021-01-01",
            "date_to": "2021-12-31",
            "fluid_type": "газ",
            "aggregation_step": "месяц"
        }
        
        response = await client.get("/api/v1/analytics/production/dynamics", params=query_params)
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверка что получили 12 месяцев
        assert len(data["reporting_dates"]) == 12
        assert data["metadata"]["response"]["total_periods"] == 12
        
        # Проверка формата дат для месячной агрегации
        reporting_dates = data["reporting_dates"]
        assert reporting_dates[0] == "2021-01"
        assert reporting_dates[-1] == "2021-12"
        
        # Каждое месторождение должно иметь 12 значений
        for field in data["fields"]:
            assert len(field["production_by_period"]) == 12
    
    @pytest.mark.asyncio
    async def test_production_dynamics_validation_errors(self, client: AsyncClient, test_data):
        """
        Тест валидации параметров запроса
        """
        # Тест неверного типа флюида
        response = await client.get("/api/v1/analytics/production/dynamics", params={
            "date_from": "2021-01-01",
            "date_to": "2023-12-31",
            "fluid_type": "неверный_тип"
        })
        assert response.status_code == 422  # Validation Error
        
        # Тест неверного шага агрегации
        response = await client.get("/api/v1/analytics/production/dynamics", params={
            "date_from": "2021-01-01",
            "date_to": "2023-12-31",
            "fluid_type": "газ",
            "aggregation_step": "неверный_шаг"
        })
        assert response.status_code == 422  # Validation Error
        
        # Тест неверного диапазона дат
        response = await client.get("/api/v1/analytics/production/dynamics", params={
            "date_from": "2023-01-01",
            "date_to": "2021-12-31",  # Конечная дата раньше начальной
            "fluid_type": "газ"
        })
        assert response.status_code == 400  # Bad Request
    
    @pytest.mark.asyncio
    async def test_production_dynamics_no_data(self, client: AsyncClient, test_data):
        """
        Тест когда нет данных для указанных параметров
        """
        query_params = {
            "date_from": "2025-01-01",  # Будущие даты
            "date_to": "2025-12-31",
            "fluid_type": "газ",
            "aggregation_step": "год"
        }
        
        response = await client.get("/api/v1/analytics/production/dynamics", params=query_params)
        
        # Должна вернуться ошибка 404 - данных не найдено
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert data["error"] == "not_found"

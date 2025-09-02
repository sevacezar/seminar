# 🧪 Тесты для Production Analysis API

## 📋 Описание

Тесты для проверки работоспособности аналитических операций API с использованием:
- **pytest** - фреймворк для тестирования
- **httpx AsyncClient** - асинхронный HTTP клиент
- **PostgreSQL в Docker** - реальная база данных для тестов

## 🚀 Подготовка к запуску

### 1. Запуск PostgreSQL в Docker
```bash
cd docker
docker-compose up -d
```

### 2. Установка зависимостей для тестирования
```bash
pip install -r requirements-test.txt
```

### 3. Проверка подключения к БД
Убедитесь что PostgreSQL доступен на `localhost:5432` с учетными данными:
- Пользователь: `postgres`
- Пароль: `postgres`
- База: `prod_analysis` (основная)
- Тестовая база: `prod_analysis_test` (создается автоматически)

## 🧪 Запуск тестов

### Запуск всех тестов
```bash
pytest tests/ -v
```

### Запуск конкретного теста
```bash
pytest tests/test_analytics.py::TestProductionDynamics::test_production_dynamics_yearly_aggregation -v
```

### Запуск с подробным выводом
```bash
pytest tests/ -v -s
```

### Запуск с покрытием кода
```bash
pytest tests/ --cov=backend --cov-report=html
```

## 📊 Структура тестов

### `conftest.py`
- **`setup_test_db`** - создание тестовой БД и таблиц
- **`db_session`** - сессия БД для каждого теста
- **`client`** - HTTP клиент с переопределенной зависимостью БД
- **`test_data`** - создание и очистка тестовых данных

### `test_analytics.py`
- **`test_production_dynamics_yearly_aggregation`** - основной тест агрегации по годам
- **`test_production_dynamics_with_field_filter`** - тест фильтрации по месторождению
- **`test_production_dynamics_with_sediment_filter`** - тест фильтрации по комплексу
- **`test_production_dynamics_monthly_aggregation`** - тест агрегации по месяцам
- **`test_production_dynamics_validation_errors`** - тест валидации параметров
- **`test_production_dynamics_no_data`** - тест отсутствия данных

## 🎯 Тестовые данные

### Создаваемые данные:
1. **2 месторождения**:
   - "Месторождение А" (оператор: Газпром)
   - "Месторождение Б" (оператор: Роснефть)

2. **2 объекта разработки**:
   - Объект А1 (сеноман) в Месторождении А
   - Объект Б1 (турон) в Месторождении Б

3. **2 флюида**:
   - Газ для каждого объекта разработки

4. **2 скважины**:
   - По одной на каждое месторождение

5. **72 записи добычи**:
   - 3 года × 12 месяцев × 2 скважины
   - Данные за 2021-2023 годы
   - Различные объемы добычи для разных месторождений

### Паттерн данных:
- **Месторождение А**: 1000 + (месяц × 10) тыс. м³
- **Месторождение Б**: 800 + (месяц × 8) тыс. м³

## ✅ Проверяемые сценарии

### 1. **Базовая агрегация**
- Агрегация по годам для всех месторождений
- Проверка структуры ответа
- Проверка метаданных
- Проверка корректности вычислений

### 2. **Фильтрация**
- По конкретному месторождению
- По комплексу отложений
- Проверка что фильтрация работает корректно

### 3. **Различные шаги агрегации**
- Годовая агрегация (3 периода)
- Месячная агрегация (12 периодов)

### 4. **Валидация**
- Неверные типы флюидов
- Неверные шаги агрегации
- Неверный диапазон дат

### 5. **Граничные случаи**
- Отсутствие данных для периода
- Проверка обработки ошибок

## 🧹 Очистка данных

После каждого теста все созданные данные автоматически удаляются:
```sql
TRUNCATE TABLE production RESTART IDENTITY CASCADE;
TRUNCATE TABLE wells RESTART IDENTITY CASCADE;
TRUNCATE TABLE fluids RESTART IDENTITY CASCADE;
TRUNCATE TABLE development_objects RESTART IDENTITY CASCADE;
TRUNCATE TABLE fields RESTART IDENTITY CASCADE;
```

## 🔍 Отладка

### Просмотр логов PostgreSQL
```bash
docker logs prod_analysis_postgres
```

### Подключение к тестовой БД
```bash
docker exec -it prod_analysis_postgres psql -U postgres -d prod_analysis_test
```

### Просмотр созданных таблиц
```sql
\dt
SELECT * FROM fields;
SELECT * FROM production LIMIT 10;
```

## ⚠️ Важные замечания

1. **PostgreSQL должен быть запущен** перед выполнением тестов
2. **Тестовая БД создается автоматически** при первом запуске
3. **Данные изолированы** - каждый тест работает с чистыми данными
4. **Enum'ы используют русские значения** согласно обновленной схеме
5. **Тесты асинхронные** - используется pytest-asyncio

## 🎉 Ожидаемый результат

При успешном выполнении все тесты должны пройти:
```
tests/test_analytics.py::TestProductionDynamics::test_production_dynamics_yearly_aggregation PASSED
tests/test_analytics.py::TestProductionDynamics::test_production_dynamics_with_field_filter PASSED
tests/test_analytics.py::TestProductionDynamics::test_production_dynamics_with_sediment_filter PASSED
tests/test_analytics.py::TestProductionDynamics::test_production_dynamics_monthly_aggregation PASSED
tests/test_analytics.py::TestProductionDynamics::test_production_dynamics_validation_errors PASSED
tests/test_analytics.py::TestProductionDynamics::test_production_dynamics_no_data PASSED

====== 6 passed in X.XXs ======
```

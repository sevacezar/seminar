# Docker Compose для Production Analysis System

Этот Docker Compose настроен для запуска полного стека приложения: фронтенд (React), бэкенд (FastAPI) и база данных (PostgreSQL).

## 🚀 Быстрый старт

### 1. Подготовка окружения

Убедитесь, что у вас есть необходимые `.env` файлы:

```bash
# Корневой .env для бэкенда и БД
cp ../.env.template ../.env
# Отредактируйте ../.env

# .env для фронтенда
# Убедитесь что ../frontend/.env существует
```

### 2. Запуск системы

```bash
# Сделать скрипты исполняемыми
chmod +x *.sh

# Запуск всех сервисов
./start.sh
```

### 3. Доступ к сервисам

- **Фронтенд**: http://localhost:3000
- **Бэкенд API**: http://localhost:8000
- **Документация API**: http://localhost:8000/docs
- **База данных**: localhost:5432

## 📋 Управление

### Основные команды

```bash
# Запуск всех сервисов
./start.sh

# Остановка всех сервисов  
./stop.sh

# Просмотр логов всех сервисов
./logs.sh

# Просмотр логов конкретного сервиса
./logs.sh backend
./logs.sh frontend
./logs.sh postgres
```

### Docker Compose команды

```bash
# Запуск в фоне
docker-compose up -d

# Запуск с пересборкой
docker-compose up --build

# Остановка
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Просмотр статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f [service_name]

# Перезапуск сервиса
docker-compose restart [service_name]
```

## 🔧 Архитектура

### Сервисы

1. **postgres** - База данных PostgreSQL 15
   - Порт: 5432
   - Volume: postgres_data
   - Health check включен

2. **backend** - FastAPI приложение
   - Порт: 8000
   - Зависит от postgres
   - Hot reload включен через volume mounting

3. **frontend** - React приложение  
   - Порт: 3000
   - Зависит от backend
   - Hot reload включен через volume mounting

### Сеть

Все сервисы работают в изолированной сети `prod_analysis_network`.

## 🛠 Разработка

### Hot Reload

- **Бэкенд**: Изменения в коде автоматически перезагружают FastAPI
- **Фронтенд**: Изменения в коде автоматически обновляют React

### Volume Mounting

Для разработки используются volume mounts:
- Исходный код монтируется в контейнеры
- Изменения отражаются мгновенно

## 🔍 Отладка

### Проблемы с запуском

1. **Проверьте .env файлы**:
   ```bash
   ls -la ../.env ../frontend/.env
   ```

2. **Проверьте порты**:
   ```bash
   netstat -tulpn | grep -E ':(3000|8000|5432)'
   ```

3. **Проверьте логи**:
   ```bash
   ./logs.sh
   ```

### Очистка

```bash
# Полная очистка (осторожно - удалит данные БД!)
docker-compose down -v
docker system prune -f

# Пересборка образов
docker-compose build --no-cache
```

## 📦 Production

Для production окружения рекомендуется:

1. Использовать отдельный docker-compose.prod.yml
2. Настроить reverse proxy (nginx)
3. Использовать secrets для паролей
4. Настроить логирование
5. Добавить мониторинг

## 🔐 Безопасность

- Все сервисы работают от непривилегированных пользователей
- База данных доступна только внутри Docker сети
- Используются health checks для проверки состояния

# Руководство по развертыванию системы аналитики добычи

## Архитектура системы

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   Database      │
│   React + TS    │◄──►│   FastAPI        │◄──►│  PostgreSQL     │
│   Port: 3000    │    │   Port: 8000     │    │   Port: 5432    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Предварительные требования

### Backend
- Python 3.9+
- PostgreSQL 12+
- pip или poetry

### Frontend
- Node.js 16+
- npm или yarn

## Пошаговое развертывание

### 1. Настройка базы данных

```sql
-- Создание базы данных
CREATE DATABASE prod_analysis;
CREATE USER prod_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE prod_analysis TO prod_user;
```

### 2. Развертывание Backend

```bash
# Переход в директорию backend
cd backend/

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл с вашими настройками

# Применение миграций
alembic upgrade head

# Запуск сервера
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Развертывание Frontend

```bash
# Переход в директорию frontend
cd frontend/

# Установка зависимостей
npm install

# Настройка переменных окружения
echo 'REACT_APP_API_URL=http://localhost:8000/api' > .env

# Запуск в режиме разработки
npm start

# Или сборка для продакшена
npm run build
```

## Конфигурация для продакшена

### Backend (.env)
```env
DATABASE_URL=postgresql://prod_user:your_secure_password@localhost:5432/prod_analysis
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]
```

### Frontend (.env)
```env
REACT_APP_API_URL=https://your-api-domain.com/api
GENERATE_SOURCEMAP=false
```

## Развертывание с Docker

### Backend Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

### Docker Compose
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: prod_analysis
      POSTGRES_USER: prod_user
      POSTGRES_PASSWORD: your_secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://prod_user:your_secure_password@db:5432/prod_analysis

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## Nginx конфигурация

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Мониторинг и логирование

### Backend логи
```python
# В main.py добавить
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Healthcheck endpoints
- Backend: `GET /health` - проверка состояния API
- Database: встроенная проверка подключения
- Frontend: статические файлы через Nginx

## Безопасность

1. **HTTPS**: Используйте SSL сертификаты
2. **CORS**: Настройте правильные origins
3. **Секреты**: Используйте менеджеры секретов
4. **Аутентификация**: Добавьте JWT токены при необходимости
5. **Rate Limiting**: Ограничьте количество запросов

## Масштабирование

### Горизонтальное масштабирование
- Несколько инстансов backend за load balancer
- CDN для статических файлов frontend
- Read replicas для базы данных

### Вертикальное масштабирование
- Увеличение ресурсов сервера
- Оптимизация запросов к БД
- Кэширование результатов

## Резервное копирование

```bash
# Backup базы данных
pg_dump -h localhost -U prod_user prod_analysis > backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U prod_user prod_analysis < backup_20240101.sql
```

## Устранение неполадок

### Частые проблемы

1. **CORS ошибки**: Проверьте настройки CORS_ORIGINS
2. **404 на API**: Убедитесь что backend запущен на правильном порту
3. **Ошибки БД**: Проверьте строку подключения DATABASE_URL
4. **Медленная загрузка**: Оптимизируйте запросы и добавьте индексы

### Команды для диагностики

```bash
# Проверка статуса сервисов
docker-compose ps

# Логи сервисов
docker-compose logs backend
docker-compose logs frontend

# Проверка подключения к БД
psql -h localhost -U prod_user -d prod_analysis -c "SELECT 1;"

# Проверка API
curl http://localhost:8000/health
```

## Обновление системы

1. Остановите сервисы
2. Обновите код
3. Примените миграции БД
4. Пересоберите образы
5. Запустите сервисы
6. Проверьте работоспособность

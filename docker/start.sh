#!/bin/bash

# Скрипт для запуска всех сервисов
echo "🚀 Запуск Production Analysis System..."

# Проверка наличия .env файлов
if [ ! -f "../.env" ]; then
    echo "❌ Файл ../.env не найден!"
    echo "📋 Создайте файл .env в корне проекта на основе .env.template"
    exit 1
fi

if [ ! -f "../frontend/.env" ]; then
    echo "❌ Файл ../frontend/.env не найден!"
    echo "📋 Создайте файл .env в папке frontend"
    exit 1
fi

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
docker-compose down

# Сборка и запуск сервисов
echo "🔨 Сборка и запуск сервисов..."
docker-compose up --build -d

# Проверка статуса
echo "📊 Проверка статуса сервисов..."
docker-compose ps

echo ""
echo "✅ Система запущена!"
echo ""
echo "🌐 Доступные сервисы:"
echo "   • Фронтенд: http://localhost:3000"
echo "   • Бэкенд API: http://localhost:8000"
echo "   • Документация API: http://localhost:8000/docs"
echo "   • База данных: localhost:5432"
echo ""
echo "📋 Полезные команды:"
echo "   • Просмотр логов: docker-compose logs -f [service_name]"
echo "   • Остановка: docker-compose down"
echo "   • Перезапуск: docker-compose restart [service_name]"
echo ""
echo "🔍 Для просмотра логов всех сервисов:"
echo "   docker-compose logs -f"

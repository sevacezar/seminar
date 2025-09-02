#!/bin/bash

# Скрипт для просмотра логов
SERVICE=${1:-""}

if [ -z "$SERVICE" ]; then
    echo "📋 Доступные сервисы:"
    echo "   • postgres"
    echo "   • backend" 
    echo "   • frontend"
    echo ""
    echo "📊 Показываем логи всех сервисов..."
    docker-compose logs -f
else
    echo "📊 Показываем логи сервиса: $SERVICE"
    docker-compose logs -f $SERVICE
fi

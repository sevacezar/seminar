#!/bin/bash

# Скрипт для остановки всех сервисов
echo "🛑 Остановка Production Analysis System..."

# Остановка и удаление контейнеров
docker-compose down

echo "✅ Все сервисы остановлены!"
echo ""
echo "💡 Для полной очистки (включая volumes):"
echo "   docker-compose down -v"
echo ""
echo "🔄 Для перезапуска используйте:"
echo "   ./start.sh"

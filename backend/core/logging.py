"""
Настройка логирования с использованием встроенного модуля logging
"""
import logging
import sys
from .config import settings


def setup_logging():
    """Настройка логирования приложения"""
    
    # Определяем уровень логирования
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Формат логов
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),  # Вывод в консоль
        ]
    )
    
    logging.info("Logging configured successfully")


def get_logger(name: str = None) -> logging.Logger:
    """Получить логгер для модуля"""
    return logging.getLogger(name or __name__)

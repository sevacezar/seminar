"""
Конфигурация приложения
"""

class Settings:
    """Настройки приложения"""
    
    # Основные настройки приложения
    APP_NAME: str = "Production Analysis API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # База данных
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/prod_analysis"
    
    # Логирование
    LOG_LEVEL: str = "INFO"


# Глобальный экземпляр настроек
settings = Settings()

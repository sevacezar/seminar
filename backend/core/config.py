"""
Конфигурация приложения
"""
import os

import dotenv

dotenv.load_dotenv()

class Settings:
    """Настройки приложения"""
    
    # Основные настройки приложения
    APP_NAME: str = "Production Analysis API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # База данных
    DB_USERNAME: str = os.getenv("DB_USERNAME")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "5432")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    
    DATABASE_URL: str = (
        f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    # Логирование
    LOG_LEVEL: str = "INFO"

    @classmethod
    def validate(cls):
        """Валидация настроек"""
        missing_vars = []
        obligatory_vars = [
            "DB_USERNAME",
            "DB_PASSWORD",
            "DB_NAME",
            "DB_PORT",
            "DB_HOST"
        ]
        for var in obligatory_vars:
            if not getattr(cls, var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"Missing variables: {", ".join(missing_vars)}")


# Глобальный экземпляр настроек
settings = Settings()

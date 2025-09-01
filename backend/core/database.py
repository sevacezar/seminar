"""
Настройка базы данных SQLAlchemy
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .config import settings
from .logging import get_logger
from .base import Base

logger = get_logger(__name__)

# Создание асинхронного движка базы данных
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Логирование SQL запросов в режиме отладки
    future=True
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Инициализация базы данных - создание всех таблиц"""
    logger.info("Initializing database")
    
    try:
        # Импортируем все модели из централизованного модуля
        import backend.core.models  # noqa: F401
        logger.info("All models imported successfully")
    except Exception as e:
        logger.error(f"Error importing models: {str(e)}")
        raise
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


async def get_db() -> AsyncSession:
    """Dependency для получения сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

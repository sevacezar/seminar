"""
Настройка базы данных SQLAlchemy
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings
from .logging import get_logger

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


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy"""
    pass


# async def init_db():
#     """Инициализация базы данных - создание всех таблиц"""
#     logger.info("Initializing database")
    
#     try:
#         # Импорт всех моделей для создания таблиц
#         from backend.entities.field.model import Field
#         from backend.entities.development_object.model import DevelopmentObject
#         from backend.entities.well.model import Well
#         from backend.entities.fluid.model import Fluid
#         from backend.entities.production.model import Production
#     except Exception as e:
#         logger.error(f"Error importing models: {str(e)}")
#         raise
    
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
    
#     logger.info("Database initialized successfully")


async def get_db() -> AsyncSession:
    """Dependency для получения сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

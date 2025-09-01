"""
Базовые классы для сервисов
"""
import logging
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from backend.core.exceptions import NotFoundError, AlreadyExistsError, ValidationError
from backend.shared.base_model import BaseModel

logger = logging.getLogger(__name__)

# Типы для generic классов
ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseService(Generic[ModelType]):
    """Базовый сервис для CRUD операций"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def create(
        self,
        db: AsyncSession,
        obj_data: Dict[str, Any],
        **kwargs
    ) -> ModelType:
        """Создание новой записи"""
        logger.info(f"Creating new record for {self.model.__name__} with data: {obj_data}")
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        logger.info(f"Record created successfully for {self.model.__name__} with id: {db_obj.id}")
        
        return db_obj
    
    async def get_by_id(
        self,
        db: AsyncSession,
        id: int,
        load_relationships: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """Получение записи по ID"""
        query = select(self.model).where(self.model.id == id)
        
        # Загрузка связанных данных если указано
        if load_relationships:
            for rel in load_relationships:
                query = query.options(selectinload(getattr(self.model, rel)))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_id_or_404(
        self,
        db: AsyncSession,
        id: int,
        load_relationships: Optional[List[str]] = None
    ) -> ModelType:
        """Получение записи по ID с исключением если не найдена"""
        obj = await self.get_by_id(db, id, load_relationships)
        if not obj:
            raise NotFoundError(f"{self.model.__name__} with id {id} not found")
        return obj
    
    async def get_multi(
        self,
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        load_relationships: Optional[List[str]] = None
    ) -> tuple[List[ModelType], int]:
        """Получение списка записей с пагинацией"""
        query = select(self.model)
        count_query = select(func.count(self.model.id))
        
        # Применение фильтров
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    attr = getattr(self.model, field)
                    if isinstance(value, list):
                        query = query.where(attr.in_(value))
                        count_query = count_query.where(attr.in_(value))
                    else:
                        query = query.where(attr == value)
                        count_query = count_query.where(attr == value)
        
        # Загрузка связанных данных если указано
        if load_relationships:
            for rel in load_relationships:
                query = query.options(selectinload(getattr(self.model, rel)))
        
        # Пагинация
        query = query.offset(offset).limit(limit)
        
        # Выполнение запросов
        result = await db.execute(query)
        items = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return list(items), total
    
    async def update(
        self,
        db: AsyncSession,
        id: int,
        update_data: Dict[str, Any]
    ) -> ModelType:
        """Обновление записи"""
        logger.info(f"Updating record for {self.model.__name__} with id: {id}, data: {update_data}")
        
        db_obj = await self.get_by_id_or_404(db, id)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        
        logger.info(f"Record updated successfully for {self.model.__name__} with id: {id}")
        
        return db_obj
    
    async def delete(
        self,
        db: AsyncSession,
        id: int
    ) -> bool:
        """Удаление записи"""
        logger.info(f"Deleting record for {self.model.__name__} with id: {id}")
        
        db_obj = await self.get_by_id_or_404(db, id)
        
        await db.delete(db_obj)
        await db.commit()
        
        logger.info(f"Record deleted successfully for {self.model.__name__} with id: {id}")
        
        return True
    
    async def bulk_create(
        self,
        db: AsyncSession,
        objects_data: List[Dict[str, Any]]
    ) -> List[ModelType]:
        """Массовое создание записей - все или никакие (транзакционно)"""
        logger.info(f"Bulk creating {len(objects_data)} records for {self.model.__name__}")
        
        created_objects = []
        
        try:
            # Создаем все объекты в рамках одной транзакции
            for i, obj_data in enumerate(objects_data):
                try:
                    db_obj = self.model(**obj_data)
                    db.add(db_obj)
                    created_objects.append(db_obj)
                except Exception as e:
                    # Если произошла ошибка, откатываем всю транзакцию
                    await db.rollback()
                    error_msg = f"Error at row {i + 1}: {str(e)}"
                    logger.error(f"Bulk create failed for {self.model.__name__}: {error_msg}")
                    raise ValidationError(error_msg, {"row": i + 1, "data": obj_data})
            
            # Если все объекты созданы успешно, коммитим
            await db.commit()
            
            # Обновляем объекты для получения ID
            for obj in created_objects:
                await db.refresh(obj)
            
            logger.info(f"Bulk create successful for {self.model.__name__}: created {len(created_objects)} records")
            return created_objects
            
        except Exception as e:
            # Гарантируем откат в случае любой ошибки
            await db.rollback()
            logger.error(f"Bulk create failed for {self.model.__name__}: {str(e)}")
            raise

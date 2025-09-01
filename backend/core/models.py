"""
Импорт всех моделей для инициализации базы данных
Этот модуль нужен для того, чтобы SQLAlchemy знал о всех таблицах
при создании схемы базы данных
"""

# Импортируем все модели здесь
from backend.entities.field.model import Field

# Когда будут созданы другие модели, добавить их сюда:
# from backend.entities.development_object.model import DevelopmentObject
# from backend.entities.well.model import Well
# from backend.entities.fluid.model import Fluid
# from backend.entities.production.model import Production

# Список всех моделей для удобства
__all__ = [
    "Field",
    # "DevelopmentObject",
    # "Well", 
    # "Fluid",
    # "Production",
]

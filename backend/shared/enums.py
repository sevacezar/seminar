"""
Перечисления (Enums) для проекта
"""
from enum import Enum


class SedimentComplexEnum(str, Enum):
    """Перечисление комплексов отложений"""
    
    TURON = "турон"
    SENOMAN = "сеноман"
    NEOKOM = "неоком"
    ACH = "ачимовка"
    
    @classmethod
    def get_values(cls):
        """Получить все возможные значения"""
        return [item.value for item in cls]
    
    @classmethod
    def get_choices(cls):
        """Получить выборы для UI"""
        return [(item.value, item.value) for item in cls]


class FluidTypeEnum(str, Enum):
    """Перечисление типов флюидов"""
    
    GAS = "газ"
    OIL = "нефть"
    CONDENSATE = "конденсат"
    
    @classmethod
    def get_values(cls):
        """Получить все возможные значения"""
        return [item.value for item in cls]


class AggregationStepEnum(str, Enum):
    """Перечисление шагов агрегации для аналитики"""
    
    MONTHLY = "месяц"
    QUARTERLY = "квартал"
    YEARLY = "год"
    
    @classmethod
    def get_values(cls):
        """Получить все возможные значения"""
        return [item.value for item in cls]

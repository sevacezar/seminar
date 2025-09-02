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


class UnitEnum(str, Enum):
    """Перечисление единиц измерения"""
    
    CUBIC_METERS = "м3"
    TONS = "т"
    
    @classmethod
    def get_values(cls):
        """Получить все возможные значения"""
        return [item.value for item in cls]
    
    @classmethod
    def get_default_unit(cls, fluid_type: 'FluidTypeEnum') -> 'UnitEnum':
        """Получить единицу измерения по умолчанию для типа флюида"""
        if fluid_type == FluidTypeEnum.GAS:
            return cls.CUBIC_METERS
        else:  # нефть и конденсат
            return cls.TONS


class AggregationStepEnum(str, Enum):
    """Перечисление шагов агрегации для аналитики"""
    
    MONTHLY = "месяц"
    QUARTERLY = "квартал"
    YEARLY = "год"
    
    @classmethod
    def get_values(cls):
        """Получить все возможные значения"""
        return [item.value for item in cls]

"""
Pydantic схемы для аналитических операций
"""
from datetime import datetime, date
from typing import List, Optional
from backend.shared.base_schema import BaseSchema
from backend.shared.enums import SedimentComplexEnum, FluidTypeEnum, AggregationStepEnum, UnitEnum


class ProductionDynamicsRequestSchema(BaseSchema):
    """Схема запроса динамики добычи"""
    date_from: date
    date_to: date
    fluid_type: FluidTypeEnum = FluidTypeEnum.GAS
    field_ids: Optional[List[int]] = None
    sediment_complexes: Optional[List[SedimentComplexEnum]] = None
    aggregation_step: AggregationStepEnum = AggregationStepEnum.YEARLY


class ProductionDynamicsMetadataRequest(BaseSchema):
    """Метаданные запроса"""
    date_from: date
    date_to: date
    fluid_type: FluidTypeEnum
    field_ids: Optional[List[int]]
    sediment_complexes: Optional[List[SedimentComplexEnum]]
    aggregation_step: AggregationStepEnum


class ProductionDynamicsMetadataResponse(BaseSchema):
    """Метаданные ответа"""
    total_fields: int
    total_periods: int
    unit: UnitEnum
    generated_at: datetime


class ProductionDynamicsMetadata(BaseSchema):
    """Общие метаданные"""
    request: ProductionDynamicsMetadataRequest
    response: ProductionDynamicsMetadataResponse


class FieldProductionData(BaseSchema):
    """Данные добычи по месторождению"""
    field_id: int
    field_name: str
    production_by_period: List[float]


class TotalProductionData(BaseSchema):
    """Суммарные данные добычи"""
    production_by_period: List[float]


class ProductionDynamicsResponseSchema(BaseSchema):
    """Схема ответа динамики добычи"""
    metadata: ProductionDynamicsMetadata
    reporting_dates: List[str]
    fields: List[FieldProductionData]
    total: TotalProductionData

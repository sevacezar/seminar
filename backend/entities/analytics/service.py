"""
Сервис для аналитических операций
"""
import logging
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from backend.entities.production.model import Production
from backend.entities.field.model import Field
from backend.entities.development_object.model import DevelopmentObject
from backend.entities.analytics.schema import (
    ProductionDynamicsResponseSchema,
    ProductionDynamicsMetadata,
    ProductionDynamicsMetadataRequest,
    ProductionDynamicsMetadataResponse,
    FieldProductionData,
    TotalProductionData
)
from backend.shared.enums import SedimentComplexEnum, FluidTypeEnum, AggregationStepEnum

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Сервис для аналитических операций"""
    
    def __init__(self):
        pass
    
    async def get_production_dynamics(
        self,
        db: AsyncSession,
        date_from: date,
        date_to: date,
        fluid_type: FluidTypeEnum = FluidTypeEnum.GAS,
        field_ids: Optional[List[int]] = None,
        sediment_complexes: Optional[List[SedimentComplexEnum]] = None,
        aggregation_step: AggregationStepEnum = AggregationStepEnum.YEARLY
    ) -> ProductionDynamicsResponseSchema:
        """Получение динамики добычи по выбранным параметрам"""
        
        logger.info(f"Getting production dynamics: {date_from} - {date_to}, fluid_type={fluid_type}")
        
        try:
            # Базовый запрос
            query = select(
                Production.field_id,
                Field.name.label("field_name"),
                func.extract('year', Production.date).label("year"),
                func.sum(Production.amount).label("total_amount")
            ).select_from(
                Production.__table__.join(Field.__table__)
            ).where(
                and_(
                    Production.date >= date_from,
                    Production.date <= date_to,
                    Production.fluid_type == fluid_type.value
                )
            )
            
            # Применение фильтров
            if field_ids:
                query = query.where(Production.field_id.in_(field_ids))
            
            if sediment_complexes:
                # Подзапрос для фильтрации по комплексам отложений
                # Преобразуем enum в строки для сравнения
                sediment_values = [complex_enum.value for complex_enum in sediment_complexes]
                subquery = select(DevelopmentObject.id).where(
                    DevelopmentObject.sediment_complex.in_(sediment_values)
                )
                query = query.where(Production.development_object_id.in_(subquery))
            
            # Группировка по полям и периодам
            if aggregation_step == AggregationStepEnum.YEARLY:
                query = query.group_by(
                    Production.field_id,
                    Field.name,
                    func.extract('year', Production.date)
                )
            elif aggregation_step == AggregationStepEnum.MONTHLY:
                query = query.add_columns(
                    func.extract('month', Production.date).label("month")
                ).group_by(
                    Production.field_id,
                    Field.name,
                    func.extract('year', Production.date),
                    func.extract('month', Production.date)
                )
            elif aggregation_step == AggregationStepEnum.QUARTERLY:
                query = query.add_columns(
                    func.extract('quarter', Production.date).label("quarter")
                ).group_by(
                    Production.field_id,
                    Field.name,
                    func.extract('year', Production.date),
                    func.extract('quarter', Production.date)
                )
            
            # Выполнение запроса
            result = await db.execute(query)
            raw_data = result.all()
            
            # Обработка данных
            fields_data = {}
            reporting_dates = set()
            
            for row in raw_data:
                field_id = row.field_id
                field_name = row.field_name
                year = int(row.year)
                amount = float(row.total_amount)
                
                # Формирование ключа периода
                if aggregation_step == AggregationStepEnum.YEARLY:
                    period_key = str(year)
                elif aggregation_step == AggregationStepEnum.MONTHLY:
                    month = int(row.month)
                    period_key = f"{year}-{month:02d}"
                elif aggregation_step == AggregationStepEnum.QUARTERLY:
                    quarter = int(row.quarter)
                    period_key = f"{year}-Q{quarter}"
                else:
                    period_key = str(year)
                
                reporting_dates.add(period_key)
                
                if field_id not in fields_data:
                    fields_data[field_id] = {
                        "field_name": field_name,
                        "periods": {}
                    }
                
                fields_data[field_id]["periods"][period_key] = amount
            
            # Сортировка периодов
            sorted_periods = sorted(list(reporting_dates))
            
            # Формирование финального ответа
            fields_response = []
            total_by_period = {}
            
            for field_id, field_info in fields_data.items():
                production_by_period = []
                
                for period in sorted_periods:
                    amount = field_info["periods"].get(period, 0.0)
                    production_by_period.append(amount)
                    
                    # Суммирование для общих данных
                    if period not in total_by_period:
                        total_by_period[period] = 0.0
                    total_by_period[period] += amount
                
                fields_response.append(FieldProductionData(
                    field_id=field_id,
                    field_name=field_info["field_name"],
                    production_by_period=production_by_period
                ))
            
            # Формирование общих данных
            total_production = [total_by_period.get(period, 0.0) for period in sorted_periods]
            
            # Определение единицы измерения
            unit = "тыс. м³" if fluid_type == FluidTypeEnum.GAS else "т"
            
            # Формирование метаданных
            metadata = ProductionDynamicsMetadata(
                request=ProductionDynamicsMetadataRequest(
                    date_from=date_from,
                    date_to=date_to,
                    fluid_type=fluid_type,
                    field_ids=field_ids,
                    sediment_complexes=sediment_complexes,
                    aggregation_step=aggregation_step
                ),
                response=ProductionDynamicsMetadataResponse(
                    total_fields=len(fields_response),
                    total_periods=len(sorted_periods),
                    unit=unit,
                    generated_at=datetime.now()
                )
            )
            
            return ProductionDynamicsResponseSchema(
                metadata=metadata,
                reporting_dates=sorted_periods,
                fields=fields_response,
                total=TotalProductionData(production_by_period=total_production)
            )
            
        except Exception as e:
            logger.error(f"Error in get_production_dynamics: {str(e)}")
            raise


# Глобальный экземпляр сервиса
analytics_service = AnalyticsService()

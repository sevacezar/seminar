"""
SQLAlchemy модель для сущности Добыча (Production)
"""
from datetime import date
from decimal import Decimal
from sqlalchemy import String, ForeignKey, Date, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.base_model import BaseModel
from backend.shared.enums import FluidTypeEnum


class Production(BaseModel):
    """Модель записи добычи"""
    
    __tablename__ = "production"
    
    # Основные поля
    well_id: Mapped[int] = mapped_column(ForeignKey("wells.id"), nullable=False, index=True)
    fluid_id: Mapped[int] = mapped_column(ForeignKey("fluids.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=3), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    fluid_type: Mapped[FluidTypeEnum] = mapped_column(
        SQLEnum(FluidTypeEnum), 
        nullable=False, 
        index=True
    )
    
    # Денормализованные поля для ускорения агрегации
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id"), nullable=False, index=True)
    development_object_id: Mapped[int] = mapped_column(
        ForeignKey("development_objects.id"), 
        nullable=False, 
        index=True
    )
    
    # Связи с другими сущностями
    well: Mapped["Well"] = relationship("Well", back_populates="production_records")
    fluid: Mapped["Fluid"] = relationship("Fluid", back_populates="production_records")
    field: Mapped["Field"] = relationship("Field", back_populates="production_records")
    development_object: Mapped["DevelopmentObject"] = relationship(
        "DevelopmentObject", 
        back_populates="production_records"
    )
    
    def __repr__(self) -> str:
        return f"<Production(id={self.id}, well_id={self.well_id}, date={self.date}, amount={self.amount})>"

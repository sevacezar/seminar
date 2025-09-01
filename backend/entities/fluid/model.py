"""
SQLAlchemy модель для сущности Флюид (Fluid)
"""
from sqlalchemy import ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.base_model import BaseModel
from backend.shared.enums import FluidTypeEnum


class Fluid(BaseModel):
    """Модель флюида"""
    
    __tablename__ = "fluids"
    
    # Основные поля
    fluid_type: Mapped[FluidTypeEnum] = mapped_column(
        SQLEnum(FluidTypeEnum), 
        nullable=False, 
        index=True
    )
    development_object_id: Mapped[int] = mapped_column(
        ForeignKey("development_objects.id"), 
        nullable=False, 
        index=True
    )
    
    # Связи с другими сущностями
    development_object: Mapped["DevelopmentObject"] = relationship(
        "DevelopmentObject", 
        back_populates="fluids"
    )
    production_records: Mapped[list["Production"]] = relationship(
        "Production", 
        back_populates="fluid",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Fluid(id={self.id}, fluid_type='{self.fluid_type}', development_object_id={self.development_object_id})>"

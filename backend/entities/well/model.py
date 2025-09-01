"""
SQLAlchemy модель для сущности Скважина (Well)
"""
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.base_model import BaseModel
from backend.shared.enums import FluidTypeEnum


class Well(BaseModel):
    """Модель скважины"""
    
    __tablename__ = "wells"
    
    # Основные поля
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id"), nullable=False, index=True)
    fluid_type: Mapped[FluidTypeEnum] = mapped_column(
        SQLEnum(FluidTypeEnum), 
        nullable=False, 
        index=True
    )
    
    # Связи с другими сущностями
    field: Mapped["Field"] = relationship(
        "Field", 
        back_populates="wells"
    )
    production_records: Mapped[list["Production"]] = relationship(
        "Production", 
        back_populates="well",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Well(id={self.id}, name='{self.name}', field_id={self.field_id}, fluid_type='{self.fluid_type}')>"

"""
SQLAlchemy модель для сущности Объект разработки (Development Object)
"""
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.base_model import BaseModel
from backend.shared.enums import SedimentComplexEnum


class DevelopmentObject(BaseModel):
    """Модель объекта разработки"""
    
    __tablename__ = "development_objects"
    
    # Основные поля
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id"), nullable=False, index=True)
    sediment_complex: Mapped[SedimentComplexEnum] = mapped_column(
        SQLEnum(SedimentComplexEnum), 
        nullable=False, 
        index=True
    )
    
    # Связи с другими сущностями
    field: Mapped["Field"] = relationship(
        "Field", 
        back_populates="development_objects"
    )
    fluids: Mapped[list["Fluid"]] = relationship(
        "Fluid", 
        back_populates="development_object",
        cascade="all, delete-orphan"
    )
    production_records: Mapped[list["Production"]] = relationship(
        "Production", 
        back_populates="development_object"
    )
    
    def __repr__(self) -> str:
        return f"<DevelopmentObject(id={self.id}, name='{self.name}', field_id={self.field_id})>"

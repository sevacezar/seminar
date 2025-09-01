"""
SQLAlchemy модель для сущности Месторождение (Field)
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.base_model import BaseModel


class Field(BaseModel):
    """Модель месторождения"""
    
    __tablename__ = "fields"
    
    # Основные поля
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    operator: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Связи с другими сущностями
    development_objects: Mapped[list["DevelopmentObject"]] = relationship(
        "DevelopmentObject", 
        back_populates="field",
        cascade="all, delete-orphan"
    )
    wells: Mapped[list["Well"]] = relationship(
        "Well", 
        back_populates="field",
        cascade="all, delete-orphan"
    )
    production_records: Mapped[list["Production"]] = relationship(
        "Production", 
        back_populates="field"
    )

    def __repr__(self) -> str:
        return f"<Field(id={self.id}, name='{self.name}', operator='{self.operator}')>"

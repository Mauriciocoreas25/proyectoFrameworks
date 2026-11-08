from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from lib.dates import ahora_utc

class PrestamoBase(SQLModel):
    id_usuario: int = Field(nullable=False, foreign_key="usuarios.id")
    id_libro: int = Field(nullable=False, foreign_key="libros.id")
    fecha_prestamo: datetime = Field(default_factory=ahora_utc)
    fecha_devolucion_esperada: Optional[datetime] = None
    fecha_devolucion_real: Optional[datetime] = None
    estado: str = Field(default="ACTIVO", max_length=20)
    observaciones: Optional[str] = Field(default=None, max_length=255)

class Prestamo(PrestamoBase, table=True):
    __tablename__ = "prestamos"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=ahora_utc)
    updated_at: Optional[datetime] = Field(default_factory=ahora_utc)

class PrestamoCreate(SQLModel):
    id_usuario: int = Field(nullable=False, foreign_key="usuarios.id")
    id_libro: int = Field(nullable=False, foreign_key="libros.id")
    fecha_devolucion_esperada: Optional[datetime] = None
    observaciones: Optional[str] = Field(default=None, max_length=255)

class DevolucionRequest(SQLModel):
    observaciones: Optional[str] = Field(default=None, max_length=255)

class PrestamoUpdatePatch(SQLModel):
    fecha_devolucion_esperada: Optional[datetime] = None
    observaciones: Optional[str] = Field(default=None, max_length=255)

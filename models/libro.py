from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class LibroBase(SQLModel):
    titulo: str = Field(nullable=False, max_length=200, min_length=1)
    isbn: Optional[str] = Field(default=None, max_length=20)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    id_autor: int = Field(nullable=False, foreign_key="autores.id")
    id_categoria: int = Field(nullable=False, foreign_key="categorias.id")
    disponible: bool = Field(default=True)
    total_ejemplares: int = Field(default=1, ge=1)
    ejemplares_disponibles: int = Field(default=1, ge=0)

class Libro(LibroBase, table=True):
    __tablename__ = "libros"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class LibroCreate(LibroBase):
    pass

class LibroUpdate(LibroBase):
    pass

class LibroUpdatePatch(SQLModel):
    titulo: Optional[str] = Field(default=None, max_length=200, min_length=1)
    isbn: Optional[str] = Field(default=None, max_length=20)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    id_autor: Optional[int] = Field(default=None)
    id_categoria: Optional[int] = Field(default=None)
    disponible: Optional[bool] = Field(default=None)
    total_ejemplares: Optional[int] = Field(default=None, ge=1)
    ejemplares_disponibles: Optional[int] = Field(default=None, ge=0)

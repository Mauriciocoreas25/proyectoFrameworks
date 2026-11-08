from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class CategoriaBase(SQLModel):
    nombre: str = Field(nullable=False, max_length=100, min_length=3)
    descripcion: Optional[str] = Field(default=None, max_length=255)

class Categoria(CategoriaBase, table=True):
    __tablename__ = "categorias"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(CategoriaBase):
    pass

class CategoriaUpdatePatch(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=100, min_length=3)
    descripcion: Optional[str] = Field(default=None, max_length=255)

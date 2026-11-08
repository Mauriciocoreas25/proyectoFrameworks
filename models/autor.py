from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from lib.dates import ahora_utc

class AutorBase(SQLModel):
    nombre: str = Field(nullable=False, max_length=150, min_length=3)
    nacionalidad: Optional[str] = Field(default=None, max_length=100)
    biografia: Optional[str] = Field(default=None, max_length=500)

class Autor(AutorBase, table=True):
    __tablename__ = "autores"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=ahora_utc)
    updated_at: Optional[datetime] = Field(default_factory=ahora_utc)

class AutorCreate(AutorBase):
    pass

class AutorUpdate(AutorBase):
    pass

class AutorUpdatePatch(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=150, min_length=3)
    nacionalidad: Optional[str] = Field(default=None, max_length=100)
    biografia: Optional[str] = Field(default=None, max_length=500)

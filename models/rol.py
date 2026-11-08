from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from lib.dates import ahora_utc

class RolBase(SQLModel):
    nombre: str = Field(nullable=False, max_length=50, min_length=3)
    descripcion: Optional[str] = Field(default=None, max_length=255)

class Rol(RolBase, table=True):
    __tablename__ = "roles"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=ahora_utc)
    updated_at: Optional[datetime] = Field(default_factory=ahora_utc)

class RolCreate(RolBase):
    pass

class RolUpdate(RolBase):
    pass

class RolUpdatePatch(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=50, min_length=3)
    descripcion: Optional[str] = Field(default=None, max_length=255)

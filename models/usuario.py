from datetime import datetime
from typing import Optional
from pydantic import EmailStr
from sqlmodel import SQLModel, Field
from lib.dates import ahora_utc

class UsuarioBase(SQLModel):
    username: str = Field(nullable=False, max_length=50, min_length=3, unique=True)
    password: str = Field(nullable=False, max_length=255, min_length=3)
    nombre: str = Field(nullable=False, max_length=100, min_length=2)
    apellido: str = Field(nullable=False, max_length=100, min_length=2)
    telefono: Optional[str] = Field(default=None, max_length=15)
    correo: Optional[EmailStr] = Field(default=None, max_length=150)
    id_rol: int = Field(nullable=False, foreign_key="roles.id")

class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuarios"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=ahora_utc)
    updated_at: Optional[datetime] = Field(default_factory=ahora_utc)

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioRead(SQLModel):
    id: int
    username: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    id_rol: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UsuarioUpdate(SQLModel):
    nombre: str = Field(nullable=False, max_length=100, min_length=2)
    apellido: str = Field(nullable=False, max_length=100, min_length=2)
    telefono: Optional[str] = Field(default=None, max_length=15)
    correo: Optional[EmailStr] = Field(default=None, max_length=150)
    id_rol: Optional[int] = Field(default=None, foreign_key="roles.id")
    password: Optional[str] = Field(default=None, min_length=3, max_length=255)

class UsuarioUpdatePatch(SQLModel):
    username: Optional[str] = Field(default=None, max_length=50, min_length=3)
    password: Optional[str] = Field(default=None, max_length=255, min_length=3)
    nombre: Optional[str] = Field(default=None, max_length=100, min_length=2)
    apellido: Optional[str] = Field(default=None, max_length=100, min_length=2)
    telefono: Optional[str] = Field(default=None, max_length=15)
    correo: Optional[EmailStr] = Field(default=None, max_length=150)
    id_rol: Optional[int] = Field(default=None)

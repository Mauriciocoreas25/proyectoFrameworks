from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select
from models.rol import Rol, RolCreate, RolUpdate, RolUpdatePatch
from models.usuario import Usuario
from config.session_Dependencia import SessionDeDependencia
from config.segurity_Dependencia import Token_Dependencia
from lib.dates import ahora_utc

router = APIRouter()

@router.get("/roles", response_model=list[Rol], status_code=status.HTTP_200_OK)
async def get_roles(
    session: SessionDeDependencia,
    token: Token_Dependencia,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
):
    if token["id_rol"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Rol).offset(offset).limit(limit)
    resultado = session.exec(consulta).all()
    return resultado

@router.get("/roles/{id}", response_model=Rol, status_code=status.HTTP_200_OK)
async def get_rol(id: int, session: SessionDeDependencia, token: Token_Dependencia):
    if token["id_rol"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Rol).where(Rol.id == id)
    rol = session.exec(consulta).first()
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    return rol

@router.post("/roles", response_model=Rol, status_code=status.HTTP_201_CREATED)
async def create_rol(
    datos_rol: RolCreate, session: SessionDeDependencia, token: Token_Dependencia
):
    if token["id_rol"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    # Validar nombre único
    consulta = select(Rol).where(Rol.nombre == datos_rol.nombre)
    if session.exec(consulta).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El rol con nombre '{datos_rol.nombre}' ya existe",
        )
    rol_nuevo = Rol(
        nombre=datos_rol.nombre,
        descripcion=datos_rol.descripcion,
    )
    session.add(rol_nuevo)
    session.commit()
    session.refresh(rol_nuevo)
    return rol_nuevo

@router.put("/roles/{id}", response_model=Rol, status_code=status.HTTP_200_OK)
async def update_rol(
    id: int, datos_rol: RolUpdate, session: SessionDeDependencia, token: Token_Dependencia
):
    if token["id_rol"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Rol).where(Rol.id == id)
    rol = session.exec(consulta).first()
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    
    rol.nombre = datos_rol.nombre
    rol.descripcion = datos_rol.descripcion
    rol.updated_at = ahora_utc()
    session.add(rol)
    session.commit()
    session.refresh(rol)
    return rol

@router.patch("/roles/{id}", response_model=Rol, status_code=status.HTTP_200_OK)
async def patch_rol(
    id: int, datos_rol: RolUpdatePatch, session: SessionDeDependencia, token: Token_Dependencia
):
    if token["id_rol"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Rol).where(Rol.id == id)
    rol = session.exec(consulta).first()
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    
    datos_dict = datos_rol.model_dump(exclude_unset=True)
    rol.sqlmodel_update(datos_dict)
    rol.updated_at = ahora_utc()
    session.add(rol)
    session.commit()
    session.refresh(rol)
    return rol

@router.delete("/roles/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rol(id: int, session: SessionDeDependencia, token: Token_Dependencia):
    if token["id_rol"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Rol).where(Rol.id == id)
    rol = session.exec(consulta).first()
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    
    # Validar integridad referencial: no eliminar si tiene usuarios asociados
    consulta_usuarios = select(Usuario).where(Usuario.id_rol == id)
    usuario_asociado = session.exec(consulta_usuarios).first()
    if usuario_asociado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el rol porque tiene usuarios asociados",
        )
    
    session.delete(rol)
    session.commit()
    return None

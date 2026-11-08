from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
import jwt

from models.usuario import (
    Usuario,
    UsuarioCreate,
    UsuarioRead,
    UsuarioUpdate,
    UsuarioUpdatePatch,
)
from models.rol import Rol
from models.prestamo import Prestamo
from config.session_Dependencia import SessionDeDependencia
from config.segurity_Dependencia import Token_Dependencia
from config.segurity import decode_access_token, oauth2_scheme
from lib.pwd import get_password_hash
from lib.dates import ahora_utc

router = APIRouter()

# Función auxiliar opcional para endpoints de registro abierto
def get_optional_current_user(token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="oauth/login", auto_error=False))) -> Optional[dict]:
    if not token:
        return None
    try:
        return decode_access_token(token)
    except Exception:
        return None

@router.get("/usuarios", response_model=list[UsuarioRead], status_code=status.HTTP_200_OK)
async def get_usuarios(
    session: SessionDeDependencia,
    token: Token_Dependencia,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
):
    # Solo Administrador (1) y Bibliotecario (2) pueden listar todos los usuarios
    if token["id_rol"] not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Usuario).offset(offset).limit(limit)
    resultado = session.exec(consulta).all()
    return resultado

@router.get("/usuarios/perfil", response_model=UsuarioRead, status_code=status.HTTP_200_OK)
async def get_mi_perfil(session: SessionDeDependencia, token: Token_Dependencia):
    consulta = select(Usuario).where(Usuario.id == token["id"])
    usuario = session.exec(consulta).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario

@router.get("/usuarios/{id}", response_model=UsuarioRead, status_code=status.HTTP_200_OK)
async def get_usuario(id: int, session: SessionDeDependencia, token: Token_Dependencia):
    # Administrador (1), Bibliotecario (2) o el propio usuario
    if token["id_rol"] not in (1, 2) and token["id"] != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Usuario).where(Usuario.id == id)
    usuario = session.exec(consulta).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario

@router.post("/usuarios", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    datos_usuario: UsuarioCreate,
    session: SessionDeDependencia,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    # Validar que el username sea único
    consulta = select(Usuario).where(Usuario.username == datos_usuario.username)
    if session.exec(consulta).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso",
        )
    
    # Validar que el rol exista
    consulta_rol = select(Rol).where(Rol.id == datos_usuario.id_rol)
    rol = session.exec(consulta_rol).first()
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado",
        )
    
    # Si quien crea no es administrador (rol 1), solo se puede registrar con rol de usuario/lector (ej. 3)
    if datos_usuario.id_rol == 1 or datos_usuario.id_rol == 2:
        if not current_user or current_user.get("id_rol") != 1:
            # Comprobar si existe algún usuario en el sistema (primer usuario administrador)
            total_usuarios = session.exec(select(Usuario)).first()
            if total_usuarios is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo un administrador puede asignar roles administrativos",
                )
    
    # Hashear contraseña
    password_hash = get_password_hash(datos_usuario.password)
    
    usuario_nuevo = Usuario(
        username=datos_usuario.username,
        password=password_hash,
        nombre=datos_usuario.nombre,
        apellido=datos_usuario.apellido,
        telefono=datos_usuario.telefono,
        correo=datos_usuario.correo,
        id_rol=datos_usuario.id_rol,
    )
    session.add(usuario_nuevo)
    session.commit()
    session.refresh(usuario_nuevo)
    return usuario_nuevo

@router.put("/usuarios/{id}", response_model=UsuarioRead, status_code=status.HTTP_200_OK)
async def update_usuario(
    id: int,
    datos_usuario: UsuarioUpdate,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    # Solo admin puede actualizar a otros usuarios; un usuario solo puede actualizar su propio perfil
    if token["id_rol"] != 1 and token["id"] != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    
    consulta = select(Usuario).where(Usuario.id == id)
    usuario = session.exec(consulta).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Si no es admin, no puede cambiar su id_rol
    if datos_usuario.id_rol is not None and token["id_rol"] != 1 and datos_usuario.id_rol != usuario.id_rol:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cambiar tu rol",
        )
    
    if datos_usuario.id_rol is not None:
        consulta_rol = select(Rol).where(Rol.id == datos_usuario.id_rol)
        if not session.exec(consulta_rol).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
        usuario.id_rol = datos_usuario.id_rol
        
    usuario.nombre = datos_usuario.nombre
    usuario.apellido = datos_usuario.apellido
    usuario.telefono = datos_usuario.telefono
    usuario.correo = datos_usuario.correo
    
    if datos_usuario.password:
        usuario.password = get_password_hash(datos_usuario.password)
        
    usuario.updated_at = ahora_utc()
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario

@router.patch("/usuarios/{id}", response_model=UsuarioRead, status_code=status.HTTP_200_OK)
async def patch_usuario(
    id: int,
    datos_usuario: UsuarioUpdatePatch,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    if token["id_rol"] != 1 and token["id"] != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Usuario).where(Usuario.id == id)
    usuario = session.exec(consulta).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Validar cambio de rol solo para admin
    if datos_usuario.id_rol is not None:
        if token["id_rol"] != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para cambiar tu rol",
            )
        consulta_rol = select(Rol).where(Rol.id == datos_usuario.id_rol)
        if not session.exec(consulta_rol).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
        usuario.id_rol = datos_usuario.id_rol
        
    # Validar si username fue enviado y es diferente
    if datos_usuario.username and datos_usuario.username != usuario.username:
        consulta_u = select(Usuario).where(Usuario.username == datos_usuario.username)
        if session.exec(consulta_u).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso",
            )
        usuario.username = datos_usuario.username
        
    if datos_usuario.password:
        usuario.password = get_password_hash(datos_usuario.password)
    if datos_usuario.nombre is not None:
        usuario.nombre = datos_usuario.nombre
    if datos_usuario.apellido is not None:
        usuario.apellido = datos_usuario.apellido
    if datos_usuario.telefono is not None:
        usuario.telefono = datos_usuario.telefono
    if datos_usuario.correo is not None:
        usuario.correo = datos_usuario.correo
        
    usuario.updated_at = ahora_utc()
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario

@router.delete("/usuarios/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(id: int, session: SessionDeDependencia, token: Token_Dependencia):
    # Solo Administrador (1) puede eliminar usuarios
    if token["id_rol"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Usuario).where(Usuario.id == id)
    usuario = session.exec(consulta).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Validar integridad referencial: no eliminar si tiene préstamos activos
    consulta_prestamos = select(Prestamo).where(
        Prestamo.id_usuario == id,
        Prestamo.estado == "ACTIVO",
    )
    prestamo_activo = session.exec(consulta_prestamos).first()
    if prestamo_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el usuario porque tiene préstamos activos pendientes de devolución",
        )
        
    session.delete(usuario)
    session.commit()
    return None

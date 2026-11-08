from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select
from models.autor import Autor, AutorCreate, AutorUpdate, AutorUpdatePatch
from models.libro import Libro
from config.session_Dependencia import SessionDeDependencia
from config.segurity_Dependencia import Token_Dependencia
from lib.dates import ahora_utc

router = APIRouter()

@router.get("/autores", response_model=list[Autor], status_code=status.HTTP_200_OK)
async def get_autores(
    session: SessionDeDependencia,
    token: Token_Dependencia,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
):
    consulta = select(Autor).offset(offset).limit(limit)
    resultado = session.exec(consulta).all()
    return resultado

@router.get("/autores/{id}", response_model=Autor, status_code=status.HTTP_200_OK)
async def get_autor(id: int, session: SessionDeDependencia, token: Token_Dependencia):
    consulta = select(Autor).where(Autor.id == id)
    autor = session.exec(consulta).first()
    if not autor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor no encontrado")
    return autor

@router.post("/autores", response_model=Autor, status_code=status.HTTP_201_CREATED)
async def create_autor(
    datos_autor: AutorCreate,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    if token["id_rol"] not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    autor_nuevo = Autor(
        nombre=datos_autor.nombre,
        nacionalidad=datos_autor.nacionalidad,
        biografia=datos_autor.biografia,
    )
    session.add(autor_nuevo)
    session.commit()
    session.refresh(autor_nuevo)
    return autor_nuevo

@router.put("/autores/{id}", response_model=Autor, status_code=status.HTTP_200_OK)
async def update_autor(
    id: int,
    datos_autor: AutorUpdate,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    if token["id_rol"] not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Autor).where(Autor.id == id)
    autor = session.exec(consulta).first()
    if not autor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor no encontrado")
    
    autor.nombre = datos_autor.nombre
    autor.nacionalidad = datos_autor.nacionalidad
    autor.biografia = datos_autor.biografia
    autor.updated_at = ahora_utc()
    
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor

@router.patch("/autores/{id}", response_model=Autor, status_code=status.HTTP_200_OK)
async def patch_autor(
    id: int,
    datos_autor: AutorUpdatePatch,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    if token["id_rol"] not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Autor).where(Autor.id == id)
    autor = session.exec(consulta).first()
    if not autor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor no encontrado")
    
    datos_dict = datos_autor.model_dump(exclude_unset=True)
    autor.sqlmodel_update(datos_dict)
    autor.updated_at = ahora_utc()
    
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor

@router.delete("/autores/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_autor(id: int, session: SessionDeDependencia, token: Token_Dependencia):
    if token["id_rol"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Autor).where(Autor.id == id)
    autor = session.exec(consulta).first()
    if not autor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor no encontrado")
    
    # Validar integridad referencial: no eliminar si tiene libros asociados
    consulta_libros = select(Libro).where(Libro.id_autor == id)
    if session.exec(consulta_libros).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el autor porque tiene libros asociados",
        )
    
    session.delete(autor)
    session.commit()
    return None

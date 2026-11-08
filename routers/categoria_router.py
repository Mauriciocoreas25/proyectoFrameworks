from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select
from models.categoria import Categoria, CategoriaCreate, CategoriaUpdate, CategoriaUpdatePatch
from models.libro import Libro
from config.session_Dependencia import SessionDeDependencia
from config.segurity_Dependencia import Token_Dependencia
from lib.dates import ahora_utc

router = APIRouter()

@router.get("/categorias", response_model=list[Categoria], status_code=status.HTTP_200_OK)
async def get_categorias(
    session: SessionDeDependencia,
    token: Token_Dependencia,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
):
    # Todos los usuarios autenticados pueden consultar las categorías
    consulta = select(Categoria).offset(offset).limit(limit)
    resultado_de_consulta = session.exec(consulta)
    return resultado_de_consulta.all()

@router.get("/categorias/{id}", response_model=Categoria, status_code=status.HTTP_200_OK)
async def get_categoria(
    id: int, session: SessionDeDependencia, token: Token_Dependencia
):
    consulta = select(Categoria).where(Categoria.id == id)
    resultado_de_consulta = session.exec(consulta).first()
    if not resultado_de_consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    return resultado_de_consulta

@router.post("/categorias", response_model=Categoria, status_code=status.HTTP_201_CREATED)
async def create_categoria(
    datos_categoria: CategoriaCreate,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    # Solo Administrador (1) o Bibliotecario (2) pueden crear categorías
    if token["id_rol"] not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    
    categoria_nueva = Categoria(
        nombre=datos_categoria.nombre,
        descripcion=datos_categoria.descripcion,
    )
    session.add(categoria_nueva)
    session.commit()
    session.refresh(categoria_nueva)
    return categoria_nueva

@router.put("/categorias/{id}", response_model=Categoria, status_code=status.HTTP_200_OK)
async def update_categoria(
    id: int,
    datos_categoria: CategoriaUpdate,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    if token["id_rol"] not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Categoria).where(Categoria.id == id)
    resultado_de_consulta = session.exec(consulta).first()
    if not resultado_de_consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    
    resultado_de_consulta.nombre = datos_categoria.nombre
    if datos_categoria.descripcion is not None:
        resultado_de_consulta.descripcion = datos_categoria.descripcion
    resultado_de_consulta.updated_at = ahora_utc()
    
    session.add(resultado_de_consulta)
    session.commit()
    session.refresh(resultado_de_consulta)
    return resultado_de_consulta

@router.patch("/categorias/{id}", response_model=Categoria, status_code=status.HTTP_200_OK)
async def patch_categoria(
    id: int,
    datos_categoria: CategoriaUpdatePatch,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    if token["id_rol"] not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Categoria).where(Categoria.id == id)
    resultado_de_consulta = session.exec(consulta).first()
    if not resultado_de_consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    
    datos_dict = datos_categoria.model_dump(exclude_unset=True)
    resultado_de_consulta.sqlmodel_update(datos_dict)
    resultado_de_consulta.updated_at = ahora_utc()
    
    session.add(resultado_de_consulta)
    session.commit()
    session.refresh(resultado_de_consulta)
    return resultado_de_consulta

@router.delete("/categorias/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(
    id: int, session: SessionDeDependencia, token: Token_Dependencia
):
    # Solo Administrador (1) puede eliminar categorías
    if token["id_rol"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Categoria).where(Categoria.id == id)
    resultado_de_consulta = session.exec(consulta).first()
    if not resultado_de_consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    
    # Validar integridad referencial: no eliminar si tiene libros asociados
    consulta_libros = select(Libro).where(Libro.id_categoria == id)
    if session.exec(consulta_libros).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la categoría porque tiene libros asociados",
        )
    
    session.delete(resultado_de_consulta)
    session.commit()
    return None

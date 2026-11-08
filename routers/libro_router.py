from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select
from models.libro import Libro, LibroCreate, LibroUpdate, LibroUpdatePatch
from models.autor import Autor
from models.categoria import Categoria
from models.prestamo import Prestamo
from config.session_Dependencia import SessionDeDependencia
from config.segurity_Dependencia import Token_Dependencia

router = APIRouter()

@router.get("/libros", response_model=list[Libro], status_code=status.HTTP_200_OK)
async def get_libros(
    session: SessionDeDependencia,
    token: Token_Dependencia,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
    id_categoria: Optional[int] = None,
    id_autor: Optional[int] = None,
    disponible: Optional[bool] = None,
):
    consulta = select(Libro)
    if id_categoria is not None:
        consulta = consulta.where(Libro.id_categoria == id_categoria)
    if id_autor is not None:
        consulta = consulta.where(Libro.id_autor == id_autor)
    if disponible is not None:
        consulta = consulta.where(Libro.disponible == disponible)
        
    consulta = consulta.offset(offset).limit(limit)
    resultado = session.exec(consulta).all()
    return resultado

@router.get("/libros/{id}", response_model=Libro, status_code=status.HTTP_200_OK)
async def get_libro(id: int, session: SessionDeDependencia, token: Token_Dependencia):
    consulta = select(Libro).where(Libro.id == id)
    libro = session.exec(consulta).first()
    if not libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    return libro

@router.post("/libros", response_model=Libro, status_code=status.HTTP_201_CREATED)
async def create_libro(
    datos_libro: LibroCreate,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    # Solo Administrador (1) o Bibliotecario (2) pueden registrar libros
    if token["id_rol"] not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    
    # Validar que el autor exista
    consulta_autor = select(Autor).where(Autor.id == datos_libro.id_autor)
    autor = session.exec(consulta_autor).first()
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Autor con id: {datos_libro.id_autor} no encontrado",
        )
    
    # Validar que la categoría exista
    consulta_cat = select(Categoria).where(Categoria.id == datos_libro.id_categoria)
    categoria = session.exec(consulta_cat).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id: {datos_libro.id_categoria} no encontrada",
        )
    
    total = datos_libro.total_ejemplares
    ejemplares_disp = datos_libro.ejemplares_disponibles
    # Si no se especificó o es mayor al total, ajustar
    if ejemplares_disp > total:
        ejemplares_disp = total
    
    libro_nuevo = Libro(
        titulo=datos_libro.titulo,
        isbn=datos_libro.isbn,
        descripcion=datos_libro.descripcion,
        id_autor=datos_libro.id_autor,
        id_categoria=datos_libro.id_categoria,
        total_ejemplares=total,
        ejemplares_disponibles=ejemplares_disp,
        disponible=(ejemplares_disp > 0),
    )
    session.add(libro_nuevo)
    session.commit()
    session.refresh(libro_nuevo)
    return libro_nuevo

@router.put("/libros/{id}", response_model=Libro, status_code=status.HTTP_200_OK)
async def update_libro(
    id: int,
    datos_libro: LibroUpdate,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    if token["id_rol"] not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Libro).where(Libro.id == id)
    libro = session.exec(consulta).first()
    if not libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    
    # Validar autor y categoría
    consulta_autor = select(Autor).where(Autor.id == datos_libro.id_autor)
    if not session.exec(consulta_autor).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Autor con id: {datos_libro.id_autor} no encontrado",
        )
    consulta_cat = select(Categoria).where(Categoria.id == datos_libro.id_categoria)
    if not session.exec(consulta_cat).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id: {datos_libro.id_categoria} no encontrada",
        )
    
    libro.titulo = datos_libro.titulo
    libro.isbn = datos_libro.isbn
    libro.descripcion = datos_libro.descripcion
    libro.id_autor = datos_libro.id_autor
    libro.id_categoria = datos_libro.id_categoria
    libro.total_ejemplares = datos_libro.total_ejemplares
    libro.ejemplares_disponibles = datos_libro.ejemplares_disponibles
    libro.disponible = (datos_libro.ejemplares_disponibles > 0)
    libro.updated_at = datetime.utcnow()
    
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro

@router.patch("/libros/{id}", response_model=Libro, status_code=status.HTTP_200_OK)
async def patch_libro(
    id: int,
    datos_libro: LibroUpdatePatch,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    if token["id_rol"] not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Libro).where(Libro.id == id)
    libro = session.exec(consulta).first()
    if not libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    
    if datos_libro.id_autor is not None:
        consulta_autor = select(Autor).where(Autor.id == datos_libro.id_autor)
        if not session.exec(consulta_autor).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Autor con id: {datos_libro.id_autor} no encontrado",
            )
            
    if datos_libro.id_categoria is not None:
        consulta_cat = select(Categoria).where(Categoria.id == datos_libro.id_categoria)
        if not session.exec(consulta_cat).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con id: {datos_libro.id_categoria} no encontrada",
            )
            
    datos_dict = datos_libro.model_dump(exclude_unset=True)
    libro.sqlmodel_update(datos_dict)
    
    # Recalcular disponibilidad según ejemplares disponibles
    if "ejemplares_disponibles" in datos_dict:
        libro.disponible = (libro.ejemplares_disponibles > 0)
        
    libro.updated_at = datetime.utcnow()
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro

@router.delete("/libros/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_libro(id: int, session: SessionDeDependencia, token: Token_Dependencia):
    # Solo Administrador (1) puede eliminar libros
    if token["id_rol"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información",
        )
    consulta = select(Libro).where(Libro.id == id)
    libro = session.exec(consulta).first()
    if not libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    
    # Validar integridad referencial: no eliminar si tiene préstamos activos
    consulta_prestamos = select(Prestamo).where(
        Prestamo.id_libro == id,
        Prestamo.estado == "ACTIVO",
    )
    if session.exec(consulta_prestamos).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el libro porque tiene préstamos activos asociados",
        )
    
    session.delete(libro)
    session.commit()
    return None

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select
from models.prestamo import Prestamo, PrestamoCreate, DevolucionRequest, PrestamoUpdatePatch
from models.libro import Libro
from models.usuario import Usuario
from config.session_Dependencia import SessionDeDependencia
from config.segurity_Dependencia import Token_Dependencia

router = APIRouter()

@router.post("/prestamos", response_model=Prestamo, status_code=status.HTTP_201_CREATED)
async def create_prestamo(
    datos_prestamo: PrestamoCreate,
    session: SessionDeDependencia,
    token: Token_Dependencia,
):
    # Si es usuario lector (3), solo puede solicitar préstamos para sí mismo
    if token["id_rol"] == 3 and datos_prestamo.id_usuario != token["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para registrar préstamos a nombre de otro usuario",
        )
    
    # 1. Validar que el usuario exista
    consulta_usuario = select(Usuario).where(Usuario.id == datos_prestamo.id_usuario)
    usuario = session.exec(consulta_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id: {datos_prestamo.id_usuario} no encontrado",
        )
        
    # 2. Validar que el libro exista
    consulta_libro = select(Libro).where(Libro.id == datos_prestamo.id_libro)
    libro = session.exec(consulta_libro).first()
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libro con id: {datos_prestamo.id_libro} no encontrado",
        )
        
    # 3. REGLA DE NEGOCIO: No se puede prestar un libro que ya se encuentre prestado o no disponible
    if not libro.disponible or libro.ejemplares_disponibles <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ejemplar no está disponible para préstamo",
        )
        
    # Registrar préstamo
    nuevo_prestamo = Prestamo(
        id_usuario=datos_prestamo.id_usuario,
        id_libro=datos_prestamo.id_libro,
        fecha_prestamo=datetime.utcnow(),
        fecha_devolucion_esperada=datos_prestamo.fecha_devolucion_esperada,
        estado="ACTIVO",
        observaciones=datos_prestamo.observaciones,
    )
    
    # Actualizar disponibilidad del libro
    libro.ejemplares_disponibles -= 1
    if libro.ejemplares_disponibles <= 0:
        libro.disponible = False
    libro.updated_at = datetime.utcnow()
    
    session.add(nuevo_prestamo)
    session.add(libro)
    session.commit()
    session.refresh(nuevo_prestamo)
    return nuevo_prestamo

@router.get("/prestamos/activos", response_model=list[Prestamo], status_code=status.HTTP_200_OK)
async def get_prestamos_activos(
    session: SessionDeDependencia,
    token: Token_Dependencia,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
):
    consulta = select(Prestamo).where(Prestamo.estado == "ACTIVO")
    # Si es lector (3), solo puede consultar sus propios préstamos
    if token["id_rol"] == 3:
        consulta = consulta.where(Prestamo.id_usuario == token["id"])
        
    consulta = consulta.offset(offset).limit(limit)
    resultado = session.exec(consulta).all()
    return resultado

@router.get("/prestamos/historial", response_model=list[Prestamo], status_code=status.HTTP_200_OK)
async def get_historial_prestamos(
    session: SessionDeDependencia,
    token: Token_Dependencia,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
    id_usuario: Optional[int] = None,
    id_libro: Optional[int] = None,
):
    consulta = select(Prestamo)
    # Si es lector (3), solo puede consultar su propio historial
    if token["id_rol"] == 3:
        consulta = consulta.where(Prestamo.id_usuario == token["id"])
    else:
        if id_usuario is not None:
            consulta = consulta.where(Prestamo.id_usuario == id_usuario)
            
    if id_libro is not None:
        consulta = consulta.where(Prestamo.id_libro == id_libro)
        
    consulta = consulta.offset(offset).limit(limit)
    resultado = session.exec(consulta).all()
    return resultado

@router.get("/prestamos/{id}", response_model=Prestamo, status_code=status.HTTP_200_OK)
async def get_prestamo(
    id: int, session: SessionDeDependencia, token: Token_Dependencia
):
    consulta = select(Prestamo).where(Prestamo.id == id)
    prestamo = session.exec(consulta).first()
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado"
        )
    if token["id_rol"] == 3 and prestamo.id_usuario != token["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para consultar préstamos de otro usuario",
        )
    return prestamo

@router.post("/prestamos/{id}/devolucion", response_model=Prestamo, status_code=status.HTTP_200_OK)
async def registrar_devolucion(
    id: int,
    session: SessionDeDependencia,
    token: Token_Dependencia,
    datos_devolucion: Optional[DevolucionRequest] = None,
):
    # Solo Administrador (1) o Bibliotecario (2) pueden registrar devoluciones
    if token["id_rol"] not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para registrar devoluciones",
        )
        
    consulta = select(Prestamo).where(Prestamo.id == id)
    prestamo = session.exec(consulta).first()
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado"
        )
        
    # REGLA DE NEGOCIO: Verificar que el préstamo esté activo
    if prestamo.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El préstamo ya ha sido devuelto previamente",
        )
        
    # Actualizar estado y fecha de devolución
    prestamo.estado = "DEVUELTO"
    prestamo.fecha_devolucion_real = datetime.utcnow()
    prestamo.updated_at = datetime.utcnow()
    if datos_devolucion and datos_devolucion.observaciones:
        prestamo.observaciones = datos_devolucion.observaciones
        
    # REGLA DE NEGOCIO: Al registrar una devolución, el libro debe volver a estar disponible
    consulta_libro = select(Libro).where(Libro.id == prestamo.id_libro)
    libro = session.exec(consulta_libro).first()
    if libro:
        libro.ejemplares_disponibles += 1
        libro.disponible = True
        libro.updated_at = datetime.utcnow()
        session.add(libro)
        
    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo

from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from config.db import crear_db_y_tablas
from routers.rol_router import router as rol_router
from routers.usuario_router import router as usuario_router
from routers.categoria_router import router as categoria_router
from routers.autor_router import router as autor_router
from routers.libro_router import router as libro_router
from routers.prestamo_router import router as prestamo_router
from oauth.oauth import router as oauth_router
import models  # Asegura que todos los modelos con table=True se registren en SQLModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea las tablas en la base de datos al iniciar el servidor
    crear_db_y_tablas()
    yield

app = FastAPI(
    title="API REST Sistema Bibliotecario",
    version="1.0.0",
    description="API REST para la administración de biblioteca: usuarios, roles, catálogo (autores, categorías, libros), préstamos y devoluciones.",
    lifespan=lifespan,
)

@app.get("/", summary="Comprobando estado de api", status_code=status.HTTP_200_OK)
async def home():
    return {
        "message": "API Sistema Bibliotecario funcionando correctamente",
        "status": "ok"
    }

# Registro de routers con sus tags correspondientes
app.include_router(oauth_router, tags=["oauth"])
app.include_router(rol_router, tags=["roles"])
app.include_router(usuario_router, tags=["usuarios"])
app.include_router(categoria_router, tags=["categorias"])
app.include_router(autor_router, tags=["autores"])
app.include_router(libro_router, tags=["libros"])
app.include_router(prestamo_router, tags=["prestamos"])

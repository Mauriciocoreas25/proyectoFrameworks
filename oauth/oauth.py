from fastapi import APIRouter, status, HTTPException
from config.session_Dependencia import SessionDeDependencia
from sqlmodel import select
from models.usuario import Usuario
from lib.pwd import verify_password
from config.segurity import create_access_token
from config.segurity_Dependencia import OAuth2FormDeDependencia

router = APIRouter()

@router.post("/oauth/login", status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2FormDeDependencia, session: SessionDeDependencia):
    username = form_data.username
    consulta = select(Usuario).where(Usuario.username == username)
    usuario = session.exec(consulta).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="username o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="username o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token(
        data={"id": usuario.id, "username": usuario.username, "id_rol": usuario.id_rol}
    )
    return {"access_token": token, "token_type": "bearer"}

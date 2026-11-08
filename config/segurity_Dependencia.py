from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from config.segurity import get_current_user

OAuth2FormDeDependencia = Annotated[OAuth2PasswordRequestForm, Depends()]
Token_Dependencia = Annotated[dict, Depends(get_current_user)]

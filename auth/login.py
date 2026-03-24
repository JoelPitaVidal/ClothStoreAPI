# auth/routers.py (o donde tengas tus rutas de autenticación)
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.database import get_db
from database.db_models import Usuario
from auth.security import verificar_password, crear_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 1. Buscar usuario por email (Swagger envía "username")
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # 2. Verificar contraseña
    if not verificar_password(form_data.password, usuario.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # 3. Crear token con el campo "sub" obligatorio
    token = crear_token({"sub": usuario.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

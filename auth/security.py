import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.database import get_db
from database.db_models import Usuario

load_dotenv()

# Clave secreta para firmar los tokens — cámbiala en .env
SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esto-en-produccion")
ALGORITHM = "HS256"
MINUTOS_EXPIRACION = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Contexto de hashing — bcrypt es el algoritmo estándar para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Le dice a FastAPI dónde está el endpoint de login para el flujo OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hashear_password(password: str) -> str:
    return pwd_context.hash(password)


def verificar_password(password_plano: str, password_hash: str) -> bool:
    return pwd_context.verify(password_plano, password_hash)


def crear_token(datos: dict) -> str:
    copia = datos.copy()
    expiracion = datetime.utcnow() + timedelta(minutes=MINUTOS_EXPIRACION)
    copia.update({"exp": expiracion})
    return jwt.encode(copia, SECRET_KEY, algorithm=ALGORITHM)


def get_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependencia reutilizable — extrae y valida el token JWT de la petición.
    Se inyecta en cualquier endpoint que requiera autenticación con Depends().
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario


def get_admin_actual(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
    """
    Dependencia para rutas exclusivas de administrador.
    Construida sobre get_usuario_actual — primero valida el token, luego el rol.
    """
    if not usuario.es_admin:
        raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
    return usuario
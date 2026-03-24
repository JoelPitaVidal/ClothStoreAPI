# routers/auth.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.database import get_db
from database.db_models import Usuario
from models import (
    UsuarioRegistro,
    UsuarioRespuesta,
    TokenRespuesta,
    EditarPerfil,
    CambiarPassword
)
from auth.security import (
    hashear_password,
    verificar_password,
    crear_token,
    get_usuario_actual
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


# ---------------------------
# REGISTRO
# ---------------------------
@router.post("/registro", response_model=UsuarioRespuesta, status_code=201)
def registro(datos: UsuarioRegistro, db: Session = Depends(get_db)):

    # 🚫 Bloqueo explícito por seguridad
    if hasattr(datos, "es_admin"):
        raise HTTPException(
            status_code=403,
            detail="No puedes asignar roles desde el registro"
        )

    # Comprobar email duplicado
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        password=hashear_password(datos.password)
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


# ---------------------------
# LOGIN
# ---------------------------
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.email == form_data.username
    ).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not verificar_password(form_data.password, usuario.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = crear_token({"sub": usuario.email})

    return {"access_token": token, "token_type": "bearer"}


# ---------------------------
# PERFIL DEL USUARIO
# ---------------------------
@router.get("/me", response_model=UsuarioRespuesta)
def mi_perfil(usuario=Depends(get_usuario_actual)):
    return usuario


# ---------------------------
# EDITAR PERFIL
# ---------------------------
@router.put("/perfil", response_model=UsuarioRespuesta)
def editar_perfil(
    datos: EditarPerfil,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_actual)
):

    # 🚫 Bloqueo absoluto de cambios a es_admin
    if hasattr(datos, "es_admin"):
        raise HTTPException(
            status_code=403,
            detail="No puedes modificar el rol de administrador desde la API"
        )

    # Comprobar email duplicado
    email_existente = db.query(Usuario).filter(
        Usuario.email == datos.email,
        Usuario.id != usuario.id
    ).first()

    if email_existente:
        raise HTTPException(status_code=400, detail="Ese email ya está en uso")

    usuario.nombre = datos.nombre
    usuario.email = datos.email

    db.commit()
    db.refresh(usuario)
    return usuario


# ---------------------------
# CAMBIAR CONTRASEÑA
# ---------------------------
@router.put("/password")
def cambiar_password(
    datos: CambiarPassword,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_actual)
):

    # Bloqueo por seguridad
    if hasattr(datos, "es_admin"):
        raise HTTPException(
            status_code=403,
            detail="No puedes modificar el rol de administrador desde la API"
        )

    # Verificar contraseña actual
    if not verificar_password(datos.password_actual, usuario.password):
        raise HTTPException(
            status_code=400,
            detail="La contraseña actual no es correcta"
        )

    usuario.password = hashear_password(datos.password_nuevo)
    db.commit()

    return {"mensaje": "Contraseña actualizada correctamente"}

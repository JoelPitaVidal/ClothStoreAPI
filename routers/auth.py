from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.database import get_db
from database.db_models import Usuario
from models import (
    UsuarioRegistro,
    UsuarioRespuesta,
    EditarPerfil,
    CambiarPassword
)
from auth.security import (
    hashear_password,
    verificar_password,
    crear_token,
    get_usuario_actual
)

router = APIRouter(tags=["Autenticación"])


# ---------------------------
# REGISTRO (POST /auth/registro)
# ---------------------------
@router.post("/registro", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def registro_usuario(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        password=hashear_password(datos.password),
        es_admin=False
    )

    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al guardar en la base de datos"
        )


# ---------------------------
# LOGIN (POST /auth/login)
# ---------------------------
@router.post("/login")
def login_usuario(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    # ✅ CORREGIDO: busca el usuario por email O por nombre de usuario
    # Así el campo "usuario" del formulario acepta cualquiera de los dos
    usuario = db.query(Usuario).filter(
        (Usuario.email == form_data.username) |
        (Usuario.nombre == form_data.username)
    ).first()

    if not usuario or not verificar_password(form_data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = crear_token({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}


# ---------------------------
# MI PERFIL (GET /auth/me)
# ---------------------------
@router.get("/me", response_model=UsuarioRespuesta)
def obtener_mi_perfil(usuario: Usuario = Depends(get_usuario_actual)):
    return usuario


# ---------------------------
# EDITAR PERFIL (PUT /auth/perfil)
# ---------------------------
@router.put("/perfil", response_model=UsuarioRespuesta)
def actualizar_perfil(
        datos: EditarPerfil,
        db: Session = Depends(get_db),
        usuario: Usuario = Depends(get_usuario_actual)
):
    if datos.email != usuario.email:
        email_en_uso = db.query(Usuario).filter(Usuario.email == datos.email).first()
        if email_en_uso:
            raise HTTPException(status_code=400, detail="El email ya está en uso por otro usuario")

    usuario.nombre = datos.nombre
    usuario.email  = datos.email

    db.commit()
    db.refresh(usuario)
    return usuario


# ---------------------------
# CAMBIAR PASSWORD (PUT /auth/password)
# ---------------------------
@router.put("/password")
def actualizar_password(
        datos: CambiarPassword,
        db: Session = Depends(get_db),
        usuario: Usuario = Depends(get_usuario_actual)
):
    if not verificar_password(datos.password_actual, usuario.password):
        raise HTTPException(
            status_code=400,
            detail="La contraseña actual no coincide"
        )

    usuario.password = hashear_password(datos.password_nuevo)
    db.commit()
    return {"mensaje": "Contraseña actualizada correctamente"}
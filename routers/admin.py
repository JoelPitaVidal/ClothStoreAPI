# routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from database.db_models import Usuario
from auth.security import get_admin_actual

router = APIRouter(prefix="/admin", tags=["Administración"])


@router.patch("/hacer-admin/{usuario_id}")
def hacer_admin(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin_actual = Depends(get_admin_actual)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.es_admin:
        return {"detail": "El usuario ya es administrador"}

    usuario.es_admin = True
    db.commit()
    db.refresh(usuario)

    return {"detail": f"El usuario {usuario.email} ahora es administrador"}

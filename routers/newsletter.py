from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.db_models import Suscriptor, Noticia
from models import SuscripcionRequest, NoticiaResponse
from typing import List

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


# Público: Suscribirse
@router.post("/suscribir")
def suscribir(datos: SuscripcionRequest, db: Session = Depends(get_db)):
    existe = db.query(Suscriptor).filter(Suscriptor.email == datos.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="Este email ya está suscrito")

    nuevo_suscriptor = Suscriptor(email=datos.email)
    db.add(nuevo_suscriptor)
    db.commit()
    return {"message": "Suscripción exitosa"}


# Público: Ver noticias
@router.get("/noticias", response_model=List[NoticiaResponse])
def obtener_noticias(db: Session = Depends(get_db)):
    return db.query(Noticia).order_by(Noticia.fecha_publicacion.desc()).all()

# Administrativo: Crear una noticia
@router.post("/noticias")
def crear_noticia(noticia: NoticiaResponse, db: Session = Depends(get_db)):
    # Nota: Usamos NoticiaResponse temporalmente como esquema de entrada
    # o puedes crear uno específico llamado NoticiaCreate en models.py
    nueva_noticia = Noticia(
        titulo=noticia.titulo,
        contenido=noticia.contenido,
        imagen_url=noticia.imagen_url,
        es_drop_exclusivo=noticia.es_drop_exclusivo
    )
    db.add(nueva_noticia)
    db.commit()
    db.refresh(nueva_noticia)
    return nueva_noticia

# Administrativo: Eliminar una noticia (Opcional, para que funcione el botón de la papelera)
@router.delete("/noticias/{noticia_id}")
def eliminar_noticia(noticia_id: int, db: Session = Depends(get_db)):
    noticia = db.query(Noticia).filter(Noticia.id == noticia_id).first()
    if not noticia:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")
    db.delete(noticia)
    db.commit()
    return {"message": "Noticia eliminada"}
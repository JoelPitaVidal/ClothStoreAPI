# routers/productos.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database.database import get_db
from database.db_models import Producto
from models import ProductoCrear, ProductoRespuesta, ActualizarStock

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("/", response_model=list[ProductoRespuesta])
def listar_productos(
    categoria_id: Optional[int] = None,
    solo_disponibles: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Producto)
    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)
    if solo_disponibles:
        query = query.filter(Producto.stock > 0)
    return query.all()


@router.get("/{producto_id}", response_model=ProductoRespuesta)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    p = db.query(Producto).filter(Producto.id == producto_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return p


@router.post("/", response_model=ProductoRespuesta, status_code=201)
def crear_producto(producto: ProductoCrear, db: Session = Depends(get_db)):
    nuevo = Producto(**producto.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.patch("/{producto_id}/stock", response_model=ProductoRespuesta)
def actualizar_stock(producto_id: int, datos: ActualizarStock, db: Session = Depends(get_db)):
    p = db.query(Producto).filter(Producto.id == producto_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    nuevo_stock = p.stock + datos.cantidad
    if nuevo_stock < 0:
        raise HTTPException(status_code=400, detail="Stock no puede ser negativo")
    p.stock = nuevo_stock
    db.commit()
    db.refresh(p)
    return p


@router.put("/{producto_id}", response_model=ProductoRespuesta)
def actualizar_producto(producto_id: int, datos: ProductoCrear, db: Session = Depends(get_db)):
    p = db.query(Producto).filter(Producto.id == producto_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for campo, valor in datos.model_dump().items():
        setattr(p, campo, valor)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    p = db.query(Producto).filter(Producto.id == producto_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(p)
    db.commit()
# routers/productos.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from auth.security import get_admin_actual
from database.database import get_db
from database.db_models import Producto, Usuario
from models import ProductoCrear, ProductoRespuesta, ActualizarStock, ProductosPaginados
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from services.cloudinary_service import subir_imagen, eliminar_imagen

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("/", response_model=list[ProductoRespuesta])
def listar_productos(
    categoria_id: Optional[int] = None,
    solo_disponibles: bool = False,
    db: Session = Depends(get_db),
    # esta es la línea que da la protección de usuário =>    _: Usuario = Depends(get_admin_actual)
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


@router.get("/", response_model=ProductosPaginados)
def listar_productos(
    categoria_id: Optional[int] = None,
    solo_disponibles: bool = False,
    busqueda: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    # Construimos la query base y vamos añadiendo filtros encadenados
    query = db.query(Producto)

    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)

    if solo_disponibles:
        query = query.filter(Producto.stock > 0)

    if busqueda:
        # ilike es LIKE pero case-insensitive — busca en nombre y descripción
        query = query.filter(Producto.nombre.ilike(f"%{busqueda}%"))

    total = query.count()  # total antes de paginar, Vue lo necesita para los controles

    productos = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "resultados": productos
    }

@router.post("/{producto_id}/imagen", response_model=ProductoRespuesta)
def subir_imagen_producto(
    producto_id: int,
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(get_admin_actual)
):
    # Comprueba que el producto existe
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Valida que el archivo es una imagen
    if not imagen.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    # Si ya tenía imagen, la elimina de Cloudinary antes de subir la nueva
    if producto.imagen_url:
        eliminar_imagen(producto.imagen_url)

    # Sube la imagen y guarda la URL en la base de datos
    archivo_bytes = imagen.file.read()
    nombre = f"producto_{producto_id}"
    producto.imagen_url = subir_imagen(archivo_bytes, nombre)

    db.commit()
    db.refresh(producto)
    return producto

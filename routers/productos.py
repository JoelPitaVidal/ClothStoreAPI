from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from auth.security import get_admin_actual
from database.database import get_db
from database.db_models import Producto, Usuario
from models import ProductoCrear, ProductoRespuesta, ActualizarStock, ProductosPaginados, MarcarExclusivo
from services.cloudinary_service import subir_imagen, eliminar_imagen

router = APIRouter(prefix="/productos", tags=["Productos"])


# 1. LISTAR Y BUSCAR (Unificado)
@router.get("/", response_model=ProductosPaginados)
def listar_productos(
        categoria_id: Optional[int] = None,
        solo_disponibles: bool = False,
        solo_exclusivos: bool = False,   # ✅ NUEVO: filtro para la vista de lanzamientos
        busqueda: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        db: Session = Depends(get_db)
):
    query = db.query(Producto)

    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)

    if solo_disponibles:
        query = query.filter(Producto.stock > 0)

    # ✅ NUEVO: devuelve solo productos marcados como exclusivos
    if solo_exclusivos:
        query = query.filter(Producto.es_exclusivo == True)

    if busqueda:
        termino = f"%{busqueda}%"
        query = query.filter(
            (Producto.nombre.ilike(termino)) | (Producto.descripcion.ilike(termino))
        )

    total = query.count()
    productos = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "resultados": productos
    }


# 2. OBTENER UNO
@router.get("/{producto_id}", response_model=ProductoRespuesta)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    p = db.query(Producto).filter(Producto.id == producto_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Reliquia no encontrada en el archivo")
    return p


# 3. CREAR (Requiere Admin)
@router.post("/", response_model=ProductoRespuesta, status_code=201)
def crear_producto(
        producto: ProductoCrear,
        db: Session = Depends(get_db),
        admin_actual: Usuario = Depends(get_admin_actual)
):
    nuevo = Producto(**producto.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# 4. ACTUALIZAR TODO (Requiere Admin)
@router.put("/{producto_id}", response_model=ProductoRespuesta)
def actualizar_producto(
        producto_id: int,
        datos: ProductoCrear,
        db: Session = Depends(get_db),
        admin_actual: Usuario = Depends(get_admin_actual)
):
    p = db.query(Producto).filter(Producto.id == producto_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for campo, valor in datos.model_dump().items():
        setattr(p, campo, valor)

    db.commit()
    db.refresh(p)
    return p


# 5. ACTUALIZAR STOCK (Patch)
@router.patch("/{producto_id}/stock", response_model=ProductoRespuesta)
def actualizar_stock(
        producto_id: int,
        datos: ActualizarStock,
        db: Session = Depends(get_db)
):
    p = db.query(Producto).filter(Producto.id == producto_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    nuevo_stock = p.stock + datos.cantidad
    if nuevo_stock < 0:
        raise HTTPException(status_code=400, detail="El stock no puede descender al vacío (negativo)")

    p.stock = nuevo_stock
    db.commit()
    db.refresh(p)
    return p


# 6. MARCAR/DESMARCAR COMO EXCLUSIVO (Requiere Admin) ✅ NUEVO
@router.patch("/{producto_id}/exclusivo", response_model=ProductoRespuesta)
def marcar_exclusivo(
        producto_id: int,
        datos: MarcarExclusivo,
        db: Session = Depends(get_db),
        admin_actual: Usuario = Depends(get_admin_actual)
):
    p = db.query(Producto).filter(Producto.id == producto_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    p.es_exclusivo = datos.es_exclusivo
    p.fecha_fin_exclusivo = datos.fecha_fin_exclusivo

    db.commit()
    db.refresh(p)
    return p


# 7. ELIMINAR (Requiere Admin)
@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(
        producto_id: int,
        db: Session = Depends(get_db),
        admin_actual: Usuario = Depends(get_admin_actual)
):
    p = db.query(Producto).filter(Producto.id == producto_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="El objeto ya no existe")

    if p.imagen_url:
        try:
            eliminar_imagen(p.imagen_url)
        except:
            pass

    db.delete(p)
    db.commit()
    return None


# 8. GESTIÓN DE IMAGEN
@router.post("/{producto_id}/imagen", response_model=ProductoRespuesta)
def subir_imagen_producto(
        producto_id: int,
        imagen: UploadFile = File(...),
        db: Session = Depends(get_db),
        admin_actual: Usuario = Depends(get_admin_actual)
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if not imagen.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    if producto.imagen_url:
        eliminar_imagen(producto.imagen_url)

    archivo_bytes = imagen.file.read()
    nombre_archivo = f"producto_{producto_id}"
    producto.imagen_url = subir_imagen(archivo_bytes, nombre_archivo)

    db.commit()
    db.refresh(producto)
    return producto
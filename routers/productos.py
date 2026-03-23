# routers/productos.py
from fastapi import APIRouter, HTTPException
from typing import Optional
from models import ProductoCrear, ProductoRespuesta, ActualizarStock

router = APIRouter(prefix="/productos", tags=["Productos"])

productos = [
    {"id": 1, "nombre": "Camiseta", "precio": 19.99, "stock": 50, "categoria_id": 1},
    {"id": 2, "nombre": "Zapatillas", "precio": 89.99, "stock": 20, "categoria_id": 2},
    {"id": 3, "nombre": "Mochila", "precio": 45.00, "stock": 15, "categoria_id": 3},
    {"id": 4, "nombre": "Pantalón", "precio": 39.99, "stock": 30, "categoria_id": 1},
    {"id": 5, "nombre": "Cinturón", "precio": 14.99, "stock": 0, "categoria_id": 3},
]
contador_id = len(productos)


@router.get("/", response_model=list[ProductoRespuesta])
def listar_productos(categoria_id: Optional[int] = None, solo_disponibles: bool = False):
    resultado = productos
    if categoria_id:
        resultado = [p for p in resultado if p["categoria_id"] == categoria_id]
    if solo_disponibles:
        resultado = [p for p in resultado if p["stock"] > 0]
    return resultado


@router.get("/{producto_id}", response_model=ProductoRespuesta)
def obtener_producto(producto_id: int):
    for p in productos:
        if p["id"] == producto_id:
            return p
    raise HTTPException(status_code=404, detail="Producto no encontrado")


@router.post("/", response_model=ProductoRespuesta, status_code=201)
def crear_producto(producto: ProductoCrear):
    global contador_id
    contador_id += 1
    nuevo = {"id": contador_id, **producto.model_dump()}
    productos.append(nuevo)
    return nuevo


@router.patch("/{producto_id}/stock", response_model=ProductoRespuesta)
def actualizar_stock(producto_id: int, datos: ActualizarStock):
    for p in productos:
        if p["id"] == producto_id:
            nuevo_stock = p["stock"] + datos.cantidad
            if nuevo_stock < 0:
                raise HTTPException(status_code=400, detail="Stock no puede ser negativo")
            p["stock"] = nuevo_stock
            return p
    raise HTTPException(status_code=404, detail="Producto no encontrado")
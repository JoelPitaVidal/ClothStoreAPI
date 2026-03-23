# routers/productos.py
from fastapi import APIRouter, HTTPException
from typing import Optional
from models import ProductoCrear, ProductoRespuesta, ActualizarStock

# Mismo patrón que categorias.py — cada router gestiona un único recurso.
router = APIRouter(prefix="/productos", tags=["Productos"])

# Datos de ejemplo en memoria. Se reemplazará por consultas a base de datos.
productos = [
    {"id": 1, "nombre": "Camiseta", "precio": 19.99, "stock": 50, "categoria_id": 1},
    {"id": 2, "nombre": "Zapatillas", "precio": 89.99, "stock": 20, "categoria_id": 2},
    {"id": 3, "nombre": "Mochila", "precio": 45.00, "stock": 15, "categoria_id": 3},
    {"id": 4, "nombre": "Pantalón", "precio": 39.99, "stock": 30, "categoria_id": 1},
    {"id": 5, "nombre": "Cinturón", "precio": 14.99, "stock": 0, "categoria_id": 3},
]

contador_id = len(productos)


# GET /productos
# Acepta dos filtros opcionales como query parameters:
#   ?categoria_id=1        → solo productos de esa categoría
#   ?solo_disponibles=true → solo productos con stock > 0
# Se pueden combinar: /productos?categoria_id=1&solo_disponibles=true
@router.get("/", response_model=list[ProductoRespuesta])
def listar_productos(categoria_id: Optional[int] = None, solo_disponibles: bool = False):
    resultado = productos  # Empezamos con la lista completa y vamos filtrando

    if categoria_id:
        resultado = [p for p in resultado if p["categoria_id"] == categoria_id]

    if solo_disponibles:
        resultado = [p for p in resultado if p["stock"] > 0]

    return resultado


# GET /productos/{producto_id}
# Devuelve un producto concreto o 404 si no existe.
@router.get("/{producto_id}", response_model=ProductoRespuesta)
def obtener_producto(producto_id: int):
    for p in productos:
        if p["id"] == producto_id:
            return p
    raise HTTPException(status_code=404, detail="Producto no encontrado")


# POST /productos
# Crea un nuevo producto. El id se genera automáticamente con el contador.
@router.post("/", response_model=ProductoRespuesta, status_code=201)
def crear_producto(producto: ProductoCrear):
    global contador_id
    contador_id += 1
    nuevo = {"id": contador_id, **producto.model_dump()}
    productos.append(nuevo)
    return nuevo


# PATCH /productos/{producto_id}/stock
# Actualiza SOLO el stock de un producto sumando la cantidad recibida.
# A diferencia de PUT, no toca el resto de campos del producto.
# La cantidad puede ser negativa para restar stock (ej: al procesar un pedido).
@router.patch("/{producto_id}/stock", response_model=ProductoRespuesta)
def actualizar_stock(producto_id: int, datos: ActualizarStock):
    for p in productos:
        if p["id"] == producto_id:
            nuevo_stock = p["stock"] + datos.cantidad

            # Validación de negocio: el stock nunca puede quedar por debajo de 0
            if nuevo_stock < 0:
                raise HTTPException(status_code=400, detail="Stock no puede ser negativo")

            p["stock"] = nuevo_stock
            return p
    raise HTTPException(status_code=404, detail="Producto no encontrado")


# PUT /productos/{producto_id}
# Reemplaza un producto completo. El cliente debe enviar todos los campos.
# El id se conserva del path parameter, no del body.
@router.put("/{producto_id}", response_model=ProductoRespuesta)
def actualizar_producto(producto_id: int, datos: ProductoCrear):
    for i, p in enumerate(productos):
        if p["id"] == producto_id:
            productos[i] = {"id": producto_id, **datos.model_dump()}
            return productos[i]
    raise HTTPException(status_code=404, detail="Producto no encontrado")


# DELETE /productos/{producto_id}
# Elimina un producto. Devuelve 204 (sin contenido) si tiene éxito.
@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int):
    for i, p in enumerate(productos):
        if p["id"] == producto_id:
            productos.pop(i)
            return
    raise HTTPException(status_code=404, detail="Producto no encontrado")
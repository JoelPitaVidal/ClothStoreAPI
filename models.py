# models.py
from pydantic import BaseModel, Field
from typing import Optional

# ─────────────────────────────────────────
# CATEGORÍAS
# ─────────────────────────────────────────

# Modelo para RECIBIR datos al crear una categoría.
# Solo contiene los campos que el cliente debe enviar — el id lo asigna el sistema.
class CategoriaCrear(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)  # ... significa obligatorio
    descripcion: Optional[str] = None                      # Campo opcional, puede no venir

# Modelo para DEVOLVER una categoría en la respuesta.
# Incluye el id, que ya existe una vez guardado en el sistema.
class CategoriaRespuesta(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

# ─────────────────────────────────────────
# PRODUCTOS
# ─────────────────────────────────────────

# Modelo para RECIBIR datos al crear o reemplazar un producto.
# gt=0 significa "greater than 0" — el precio no puede ser 0 ni negativo.
# ge=0 significa "greater or equal 0" — el stock puede ser 0 pero no negativo.
class ProductoCrear(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    precio: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)  # Si no se envía stock, se asume 0
    categoria_id: int                    # Debe coincidir con el id de una categoría existente
    imagen_url: Optional[str] = None  # ← nuevo


# Modelo para DEVOLVER un producto en la respuesta.
# Separarlo de ProductoCrear permite controlar exactamente qué campos expone la API.
class ProductoRespuesta(BaseModel):
    id: int
    nombre: str
    precio: float
    stock: int
    imagen_url: Optional[str] = None  # ← nuevo
    categoria_id: int

# Modelo específico para actualizar solo el stock de un producto.
# Usar un modelo propio en lugar de un query param permite documentarlo mejor en /docs
# y añadir validaciones más adelante si fuera necesario.
class ActualizarStock(BaseModel):
    cantidad: int = Field(..., description="Positivo para añadir stock, negativo para restar")

class UsuarioRegistro(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)

from pydantic import BaseModel, Field, ConfigDict

class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    es_admin: bool

class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProductosPaginados(BaseModel):
    total: int
    skip: int
    limit: int
    resultados: list[ProductoRespuesta]

class CarritoItemRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:          int
    producto_id: int
    cantidad:    int
    producto:    ProductoRespuesta  # devuelve el producto completo, no solo el id

class CarritoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:         int
    usuario_id: int
    items:      list[CarritoItemRespuesta]
    total:      float = 0.0  # se calcula en el endpoint, no se guarda en DB

class AñadirItemCarrito(BaseModel):
    producto_id: int
    cantidad:    int = Field(default=1, ge=1)

class ActualizarItemCarrito(BaseModel):
    cantidad: int = Field(..., ge=1)

class EditarPerfil(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., min_length=5)

class CambiarPassword(BaseModel):
    password_actual: str
    password_nuevo: str = Field(..., min_length=6)


from datetime import datetime

class PedidoItemRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:          int
    producto_id: int
    cantidad:    int
    precio:      float
    producto:    ProductoRespuesta


class PedidoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:         int
    usuario_id: int
    estado:     str
    total:      float
    fecha:      datetime
    items:      list[PedidoItemRespuesta]


class ActualizarEstadoPedido(BaseModel):
    estado: str = Field(..., description="pendiente, pagado, enviado, entregado, cancelado")
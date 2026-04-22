from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ─────────────────────────────────────────
# CATEGORÍAS
# ─────────────────────────────────────────

class CategoriaCrear(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    descripcion: Optional[str] = None


class CategoriaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: Optional[str] = None


# ─────────────────────────────────────────
# PRODUCTOS
# ─────────────────────────────────────────

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = None
    precio: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    categoria_id: int
    imagen_url: Optional[str] = None
    # ✅ NUEVO: campos de lanzamiento exclusivo
    es_exclusivo: bool = False
    fecha_fin_exclusivo: Optional[datetime] = None


class ProductoCrear(ProductoBase):
    pass


class ProductoRespuesta(ProductoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProductosPaginados(BaseModel):
    total: int
    skip: int
    limit: int
    resultados: List[ProductoRespuesta]


class ActualizarStock(BaseModel):
    cantidad: int = Field(..., description="Positivo para añadir stock, negativo para restar")


# ✅ NUEVO: schema para activar/desactivar exclusivo desde el admin
class MarcarExclusivo(BaseModel):
    es_exclusivo: bool
    fecha_fin_exclusivo: Optional[datetime] = None


# ─────────────────────────────────────────
# USUARIOS Y AUTH
# ─────────────────────────────────────────

class UsuarioRegistro(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    email: str
    es_admin: bool


class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EditarPerfil(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., min_length=5)


class CambiarPassword(BaseModel):
    password_actual: str
    password_nuevo: str = Field(..., min_length=6)


# ─────────────────────────────────────────
# CARRITO
# ─────────────────────────────────────────

class CarritoItemRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    producto_id: int
    cantidad: int
    producto: ProductoRespuesta


class CarritoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    items: List[CarritoItemRespuesta]
    total: float = 0.0


class AñadirItemCarrito(BaseModel):
    producto_id: int
    cantidad: int = Field(default=1, ge=1)


class ActualizarItemCarrito(BaseModel):
    cantidad: int = Field(..., ge=1)


# ─────────────────────────────────────────
# PEDIDOS
# ─────────────────────────────────────────

class PedidoItemRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    producto_id: int
    cantidad: int
    precio: float
    producto: ProductoRespuesta


class PedidoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    estado: str
    total: float
    fecha: datetime
    # ✅ NUEVOS CAMPOS: Para que el frontend pueda ver los IDs de transacción
    stripe_payment_id: Optional[str] = None
    paypal_order_id: Optional[str] = None
    fecha_pago: Optional[datetime] = None
    items: List[PedidoItemRespuesta]


class ActualizarEstadoPedido(BaseModel):
    estado: str = Field(..., description="pendiente, pagado, enviado, entregado, cancelado")

# ✅ NUEVO: Para la respuesta del Intento de Pago
class StripeIntentRespuesta(BaseModel):
    clientSecret: str



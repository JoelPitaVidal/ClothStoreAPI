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
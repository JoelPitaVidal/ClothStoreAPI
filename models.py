# models.py
from pydantic import BaseModel, Field
from typing import Optional

class CategoriaCrear(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    descripcion: Optional[str] = None

class CategoriaRespuesta(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

class ProductoCrear(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    precio: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    categoria_id: int

class ProductoRespuesta(BaseModel):
    id: int
    nombre: str
    precio: float
    stock: int
    categoria_id: int

class ActualizarStock(BaseModel):
    cantidad: int = Field(..., description="Puede ser positivo (añadir) o negativo (restar)")
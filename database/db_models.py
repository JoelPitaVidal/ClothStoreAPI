# db_models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String, nullable=False, unique=True)
    descripcion = Column(String, nullable=True)

    # Relación inversa — permite acceder a categoria.productos directamente.
    # No crea ninguna columna extra en la tabla.
    productos = relationship("Producto", back_populates="categoria")

class Producto(Base):
    __tablename__ = "productos"

    id           = Column(Integer, primary_key=True, index=True)
    nombre       = Column(String, nullable=False)
    precio       = Column(Float, nullable=False)
    stock        = Column(Integer, default=0)

    # Clave foránea — vincula cada producto con una categoría.
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)

    # Relación directa — permite acceder a producto.categoria directamente.
    categoria = relationship("Categoria", back_populates="productos")
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Enum
from datetime import datetime
import enum


# ─────────────────────────────────────────
# USUARIOS
# ─────────────────────────────────────────
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    password = Column(String, nullable=False)
    es_admin = Column(Boolean, default=False)

    # Relaciones explícitas
    carrito = relationship("Carrito", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    pedidos = relationship("Pedido", back_populates="usuario")


# ─────────────────────────────────────────
# CATEGORÍAS Y PRODUCTOS
# ─────────────────────────────────────────
class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(String, nullable=True)

    productos = relationship("Producto", back_populates="categoria")


class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    imagen_url = Column(String, nullable=True)
    es_exclusivo = Column(Boolean, default=False, nullable=False)
    fecha_fin_exclusivo = Column(DateTime, nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)

    categoria = relationship("Categoria", back_populates="productos")


# ─────────────────────────────────────────
# CARRITO
# ─────────────────────────────────────────
class Carrito(Base):
    __tablename__ = "carritos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)

    usuario = relationship("Usuario", back_populates="carrito")
    items = relationship("CarritoItem", back_populates="carrito", cascade="all, delete-orphan")


class CarritoItem(Base):
    __tablename__ = "carrito_items"
    id = Column(Integer, primary_key=True, index=True)
    carrito_id = Column(Integer, ForeignKey("carritos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)

    carrito = relationship("Carrito", back_populates="items")
    producto = relationship("Producto")


# ─────────────────────────────────────────
# PEDIDOS Y PAGOS
# ─────────────────────────────────────────
class EstadoPedido(str, enum.Enum):
    pendiente = "pendiente"
    pagado = "pagado"
    enviado = "enviado"
    entregado = "entregado"
    cancelado = "cancelado"


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    estado = Column(Enum(EstadoPedido), default=EstadoPedido.pendiente, nullable=False)
    total = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Campos de Pasarelas (Stripe/PayPal)
    stripe_payment_id = Column(String, nullable=True, unique=True)
    paypal_order_id = Column(String, nullable=True, unique=True)
    fecha_pago = Column(DateTime, nullable=True)

    usuario = relationship("Usuario", back_populates="pedidos")
    items = relationship("PedidoItem", back_populates="pedido", cascade="all, delete-orphan")


class PedidoItem(Base):
    __tablename__ = "pedido_items"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)

    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")
# routers/pedidos.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.db_models import Pedido, PedidoItem, Carrito, Producto, EstadoPedido
from models import PedidoRespuesta, ActualizarEstadoPedido
from auth.security import get_usuario_actual, get_admin_actual

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


# POST /pedidos — confirmar carrito y crear pedido
@router.post("/", response_model=PedidoRespuesta, status_code=201)
def crear_pedido(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_actual)
):
    # Obtiene el carrito del usuario
    carrito = db.query(Carrito).filter(Carrito.usuario_id == usuario.id).first()

    if not carrito or not carrito.items:
        raise HTTPException(status_code=400, detail="El carrito está vacío")

    # Verifica stock suficiente para todos los items antes de procesar
    for item in carrito.items:
        producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
        if producto.stock < item.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock}"
            )

    # Calcula el total y crea el pedido
    total = sum(item.producto.precio * item.cantidad for item in carrito.items)

    pedido = Pedido(usuario_id=usuario.id, total=total)
    db.add(pedido)
    db.flush()  # obtiene el id del pedido sin hacer commit todavía

    # Crea los items del pedido y descuenta el stock
    for item in carrito.items:
        pedido_item = PedidoItem(
            pedido_id=pedido.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio=item.producto.precio  # precio en el momento de la compra
        )
        db.add(pedido_item)

        # Descuenta el stock ahora que se confirma el pedido
        item.producto.stock -= item.cantidad

    # Vacía el carrito tras confirmar el pedido
    for item in carrito.items:
        db.delete(item)

    db.commit()
    db.refresh(pedido)
    return pedido


# GET /pedidos — historial de pedidos del usuario autenticado
@router.get("/", response_model=list[PedidoRespuesta])
def mis_pedidos(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_actual)
):
    return db.query(Pedido).filter(Pedido.usuario_id == usuario.id).all()


# GET /pedidos/{pedido_id} — detalle de un pedido concreto
@router.get("/{pedido_id}", response_model=PedidoRespuesta)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_actual)
):
    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id,
        Pedido.usuario_id == usuario.id  # un usuario solo puede ver sus propios pedidos
    ).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


# GET /pedidos/admin/todos — todos los pedidos (solo admin)
@router.get("/admin/todos", response_model=list[PedidoRespuesta])
def todos_los_pedidos(
    db: Session = Depends(get_db),
    _=Depends(get_admin_actual)
):
    return db.query(Pedido).all()


# PATCH /pedidos/{pedido_id}/estado — actualizar estado (solo admin)
@router.patch("/{pedido_id}/estado", response_model=PedidoRespuesta)
def actualizar_estado(
    pedido_id: int,
    datos: ActualizarEstadoPedido,
    db: Session = Depends(get_db),
    _=Depends(get_admin_actual)
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Valida que el estado es uno de los permitidos
    try:
        pedido.estado = EstadoPedido(datos.estado)
    except ValueError:
        raise HTTPException(status_code=400, detail="Estado no válido")

    db.commit()
    db.refresh(pedido)
    return pedido
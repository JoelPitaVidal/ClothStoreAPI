from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.db_models import Pedido, PedidoItem, Carrito, Producto, EstadoPedido
from models import PedidoRespuesta, ActualizarEstadoPedido
from auth.security import get_usuario_actual, get_admin_actual

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=PedidoRespuesta, status_code=201)
def crear_pedido(db: Session = Depends(get_db), usuario=Depends(get_usuario_actual)):
    # 1. Obtener el carrito
    carrito = db.query(Carrito).filter(Carrito.usuario_id == usuario.id).first()

    # 2. Si el carrito está vacío, verificamos si ya hay un pedido pendiente hoy
    if not carrito or not carrito.items:
        pedido_existente = db.query(Pedido).filter(
            Pedido.usuario_id == usuario.id,
            Pedido.estado == EstadoPedido.pendiente
        ).order_by(Pedido.id.desc()).first()

        if pedido_existente:
            return pedido_existente  # Devolvemos el que ya existe para no fallar

        raise HTTPException(status_code=400, detail="El carrito está vacío y no hay pedidos pendientes")

    # 3. Verificar stock
    for item in carrito.items:
        if item.producto.stock < item.cantidad:
            raise HTTPException(status_code=400, detail=f"No hay stock de {item.producto.nombre}")

    try:
        total = sum(item.producto.precio * item.cantidad for item in carrito.items)
        pedido = Pedido(usuario_id=usuario.id, total=total, estado=EstadoPedido.pendiente)
        db.add(pedido)
        db.flush()

        for item in carrito.items:
            db.add(PedidoItem(pedido_id=pedido.id, producto_id=item.producto_id,
                              cantidad=item.cantidad, precio=item.producto.precio))
            item.producto.stock -= item.cantidad
            db.delete(item)  # Vaciamos el carrito

        db.commit()
        db.refresh(pedido)
        return pedido
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno")

# ... (Resto de rutas get_pedidos, obtener_pedido, etc. se mantienen igual)
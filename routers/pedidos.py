from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from database.database import get_db
from database.db_models import Pedido, PedidoItem, Carrito, Producto, EstadoPedido, CarritoItem  # ← todo junto
from models import PedidoRespuesta
from auth.security import get_usuario_actual

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=PedidoRespuesta, status_code=201)
def crear_pedido(db: Session = Depends(get_db), usuario=Depends(get_usuario_actual)):
    # 1. Obtener carrito con sus items y productos
    carrito = db.query(Carrito).options(
        joinedload(Carrito.items).joinedload(CarritoItem.producto)  # ✅ CarritoItem, no PedidoItem
    ).filter(Carrito.usuario_id == usuario.id).first()

    # 2. Recuperación si el carrito está vacío (Manejo de F5/Recargas)
    if not carrito or not carrito.items:
        pedido_existente = db.query(Pedido).options(
            joinedload(Pedido.items).joinedload(PedidoItem.producto)
        ).filter(
            Pedido.usuario_id == usuario.id,
            Pedido.estado == EstadoPedido.pendiente
        ).order_by(Pedido.id.desc()).first()

        if pedido_existente:
            return pedido_existente

        raise HTTPException(status_code=400, detail="El carrito está vacío y no hay pedidos pendientes.")

    ahora = datetime.utcnow()

    # 3. Validaciones de Negocio (Stock y Drops)
    for item in carrito.items:
        producto = item.producto
        if not producto:
            continue

        if producto.stock < item.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente: {producto.nombre}. Disponible: {producto.stock}"
            )

        if getattr(producto, 'es_exclusivo', False):
            if producto.fecha_fin_exclusivo and ahora > producto.fecha_fin_exclusivo:
                raise HTTPException(status_code=400, detail=f"El drop {producto.nombre} ha terminado.")

    try:
        total_pedido = sum(item.producto.precio * item.cantidad for item in carrito.items)

        # 4. Crear el Pedido — campo es 'fecha', NO 'fecha_pedido' ✅
        nuevo_pedido = Pedido(
            usuario_id=usuario.id,
            total=total_pedido,
            estado=EstadoPedido.pendiente,
            fecha=ahora  # ✅ corregido
        )
        db.add(nuevo_pedido)
        db.flush()

        # 5. Mover items del Carrito al Pedido y actualizar Stock
        for item in carrito.items:
            pedido_item = PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio=item.producto.precio
            )
            db.add(pedido_item)
            item.producto.stock -= item.cantidad
            db.delete(item)

        db.commit()

        # 6. Retorno con todos los joins necesarios
        pedido_final = db.query(Pedido).options(
            joinedload(Pedido.items).joinedload(PedidoItem.producto)
        ).filter(Pedido.id == nuevo_pedido.id).first()

        return pedido_final

    except Exception as e:
        db.rollback()
        print(f"--- ERROR CRÍTICO EN POST /PEDIDOS/ ---")
        print(f"Tipo: {type(e).__name__} | Mensaje: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al procesar el pedido.")
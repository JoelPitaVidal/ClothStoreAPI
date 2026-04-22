import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from sqlalchemy.orm import Session
from datetime import datetime

from database.database import get_db
from database import db_models as models
from auth.security import get_usuario_actual
from pydantic import BaseModel

router = APIRouter(prefix="/pagos", tags=["Pagos"])

# ⚠️ RECOMENDACIÓN: Mueve estas claves a un archivo .env
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


# Esquema para recibir datos de PayPal desde el Frontend
class PayPalRequest(BaseModel):
    order_id: str
    pedido_id: int


# --- ENDPOINTS DE STRIPE ---

@router.post("/stripe/crear-intento")
async def crear_intento_pago(
        pedido_id: int,
        db: Session = Depends(get_db),
        usuario_actual: models.Usuario = Depends(get_usuario_actual)
):
    # 1. Buscar el pedido y verificar propiedad
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id,
        models.Pedido.usuario_id == usuario_actual.id
    ).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado o no autorizado")

    if pedido.estado == models.EstadoPedido.pagado:
        raise HTTPException(status_code=400, detail="El pedido ya ha sido pagado")

    try:
        # 2. Crear el PaymentIntent (Stripe usa céntimos)
        total_centimos = int(pedido.total * 100)

        intent = stripe.PaymentIntent.create(
            amount=total_centimos,
            currency="eur",
            automatic_payment_methods={"enabled": True},
            metadata={
                "pedido_id": pedido.id,
                "usuario_id": usuario_actual.id
            }
        )

        # 3. Guardar el ID de stripe en el pedido
        pedido.stripe_payment_id = intent.id
        db.commit()

        return {"clientSecret": intent.client_secret}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error con Stripe: {str(e)}")


@router.post("/webhook")
async def stripe_webhook(
        request: Request,
        stripe_signature: str = Header(None),
        db: Session = Depends(get_db)
):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Error de validación de firma")

    # Si el pago fue exitoso en Stripe
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        pedido_id = payment_intent['metadata'].get('pedido_id')

        if pedido_id:
            pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
            if pedido and pedido.estado != models.EstadoPedido.pagado:
                pedido.estado = models.EstadoPedido.pagado
                pedido.fecha_pago = datetime.utcnow()
                db.commit()
                print(f"✅ Pedido {pedido_id} pagado con éxito (Stripe).")

    return {"status": "success"}


# --- ENDPOINTS DE PAYPAL ---

@router.post("/paypal/verificar")
async def verificar_pago_paypal(
        datos: PayPalRequest,
        db: Session = Depends(get_db),
        usuario_actual: models.Usuario = Depends(get_usuario_actual)
):
    # Buscar pedido
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == datos.pedido_id,
        models.Pedido.usuario_id == usuario_actual.id
    ).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if pedido.estado == models.EstadoPedido.pagado:
        return {"status": "success", "message": "El pedido ya figuraba como pagado"}

    try:
        # Actualizar información de pago
        pedido.estado = models.EstadoPedido.pagado
        pedido.paypal_order_id = datos.order_id
        pedido.fecha_pago = datetime.utcnow()

        db.commit()
        return {"status": "success", "message": "Pago de PayPal registrado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno al registrar el pago")
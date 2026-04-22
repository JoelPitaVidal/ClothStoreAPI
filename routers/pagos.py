import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from fpdf import FPDF
from pathlib import Path

from database.database import get_db
from database import db_models as models
from auth.security import get_usuario_actual
from pydantic import BaseModel

router = APIRouter(prefix="/pagos", tags=["Pagos"])

# Configuración de Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Carpeta para guardar facturas
FACTURAS_DIR = Path("facturas")
FACTURAS_DIR.mkdir(exist_ok=True)


class PayPalRequest(BaseModel):
    order_id: str
    pedido_id: int


# --- UTILIDAD: GENERAR FACTURA PDF ---

def generar_factura_pdf(pedido: models.Pedido):
    """Genera un archivo PDF para el pedido y devuelve la ruta."""
    # Usamos latin-1 para evitar errores con caracteres especiales si no cargamos fuentes Unicode
    pdf = FPDF()
    pdf.add_page()

    # Estilo Gótico / Elegante (Fondo Negro)
    pdf.set_fill_color(15, 15, 15)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(224, 213, 232)  # Color e0d5e8

    # Encabezado - Midnight Attire
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 20, "MIDNIGHT ATTIRE", ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Factura ID: #INV-{pedido.id}", ln=True, align='R')
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')

    pdf.ln(10)
    # Limpiamos posibles caracteres raros del email
    email_cliente = pedido.usuario.email.encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(0, 10, f"Cliente: {email_cliente}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Tabla de productos
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Producto", border=0)
    pdf.cell(40, 10, "Cant.", border=0)
    pdf.cell(40, 10, "Precio", border=0, ln=True)

    pdf.set_font("Arial", '', 11)
    for item in pedido.items:
        # Reemplazamos caracteres conflictivos en el nombre del producto
        nombre_prod = item.producto.nombre.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(100, 10, f"{nombre_prod}")
        pdf.cell(40, 10, f"{item.cantidad}")
        # IMPORTANTE: Usamos 'EUR' en lugar de '€' para evitar el crash de encode
        pdf.cell(40, 10, f"{item.precio:.2f} EUR", ln=True)

    pdf.ln(10)
    pdf.set_draw_color(224, 213, 232)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 15, f"TOTAL: {pedido.total:.2f} EUR", ln=True, align='R')

    filename = f"factura_{pedido.id}.pdf"
    filepath = FACTURAS_DIR / filename

    # Guardamos el archivo
    pdf.output(str(filepath))
    return str(filepath)


# --- ENDPOINTS DE STRIPE ---

@router.post("/stripe/crear-intento")
async def crear_intento_pago(
        pedido_id: int,
        db: Session = Depends(get_db),
        usuario_actual: models.Usuario = Depends(get_usuario_actual)
):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id,
        models.Pedido.usuario_id == usuario_actual.id
    ).first()

    if not pedido or pedido.estado == models.EstadoPedido.pagado:
        raise HTTPException(status_code=400, detail="Pedido no disponible para pago")

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(pedido.total * 100),
            currency="eur",
            automatic_payment_methods={"enabled": True},
            metadata={"pedido_id": pedido.id}
        )
        pedido.stripe_payment_id = intent.id
        db.commit()
        return {"clientSecret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(
        request: Request,
        stripe_signature: str = Header(None),
        db: Session = Depends(get_db)
):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except:
        raise HTTPException(status_code=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        pedido_id = payment_intent['metadata'].get('pedido_id')

        pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
        if pedido and pedido.estado != models.EstadoPedido.pagado:
            pedido.estado = models.EstadoPedido.pagado
            pedido.fecha_pago = datetime.utcnow()
            generar_factura_pdf(pedido)
            db.commit()

    return {"status": "success"}


# --- ENDPOINTS DE PAYPAL ---

@router.post("/paypal/verificar")
async def verificar_pago_paypal(
        datos: PayPalRequest,
        db: Session = Depends(get_db),
        usuario_actual: models.Usuario = Depends(get_usuario_actual)
):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == datos.pedido_id,
        models.Pedido.usuario_id == usuario_actual.id
    ).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if pedido.estado != models.EstadoPedido.pagado:
        pedido.estado = models.EstadoPedido.pagado
        pedido.paypal_order_id = datos.order_id
        pedido.fecha_pago = datetime.utcnow()
        generar_factura_pdf(pedido)
        db.commit()

    return {"status": "success"}


# --- ENDPOINT DESCARGA ---

@router.get("/descargar-factura/{pedido_id}")
async def descargar_factura(
        pedido_id: int,
        db: Session = Depends(get_db),
        usuario_actual: models.Usuario = Depends(get_usuario_actual)
):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if pedido.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    path = FACTURAS_DIR / f"factura_{pedido.id}.pdf"

    # Forzamos regeneración si no existe o hubo error previo
    if not path.exists():
        generar_factura_pdf(pedido)

    return FileResponse(
        path=path,
        filename=f"Factura_Midnight_{pedido_id}.pdf",
        media_type='application/pdf'
    )
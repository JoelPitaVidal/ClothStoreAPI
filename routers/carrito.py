# routers/carrito.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.db_models import Carrito, CarritoItem, Producto
from models import CarritoRespuesta, AñadirItemCarrito, ActualizarItemCarrito
from auth.security import get_usuario_actual

router = APIRouter(prefix="/carrito", tags=["Carrito"])


def get_or_create_carrito(usuario_id: int, db: Session) -> Carrito:
    """
    Busca el carrito del usuario. Si no existe, lo crea automáticamente.
    De esta forma el usuario no necesita 'crear' el carrito manualmente.
    """
    carrito = db.query(Carrito).filter(Carrito.usuario_id == usuario_id).first()
    if not carrito:
        carrito = Carrito(usuario_id=usuario_id)
        db.add(carrito)
        db.commit()
        db.refresh(carrito)
    return carrito


def calcular_total(carrito: Carrito) -> float:
    """Suma precio * cantidad de cada item del carrito."""
    return sum(item.producto.precio * item.cantidad for item in carrito.items)


# GET /carrito — ver el carrito del usuario autenticado
@router.get("/", response_model=CarritoRespuesta)
def ver_carrito(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_actual)
):
    carrito = get_or_create_carrito(usuario.id, db)
    respuesta = CarritoRespuesta.model_validate(carrito)
    respuesta.total = calcular_total(carrito)
    return respuesta


# POST /carrito/items — añadir un producto al carrito
@router.post("/items", response_model=CarritoRespuesta, status_code=201)
def añadir_item(
    datos: AñadirItemCarrito,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_actual)
):
    # Comprueba que el producto existe
    producto = db.query(Producto).filter(Producto.id == datos.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    carrito = get_or_create_carrito(usuario.id, db)

    # Si el producto ya está en el carrito, suma la cantidad
    item_existente = db.query(CarritoItem).filter(
        CarritoItem.carrito_id == carrito.id,
        CarritoItem.producto_id == datos.producto_id
    ).first()

    if item_existente:
        item_existente.cantidad += datos.cantidad
    else:
        nuevo_item = CarritoItem(
            carrito_id=carrito.id,
            producto_id=datos.producto_id,
            cantidad=datos.cantidad
        )
        db.add(nuevo_item)

    db.commit()
    db.refresh(carrito)

    respuesta = CarritoRespuesta.model_validate(carrito)
    respuesta.total = calcular_total(carrito)
    return respuesta


# PATCH /carrito/items/{item_id} — cambiar la cantidad de un item
@router.patch("/items/{item_id}", response_model=CarritoRespuesta)
def actualizar_item(
    item_id: int,
    datos: ActualizarItemCarrito,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_actual)
):
    carrito = get_or_create_carrito(usuario.id, db)

    item = db.query(CarritoItem).filter(
        CarritoItem.id == item_id,
        CarritoItem.carrito_id == carrito.id  # seguridad: el item debe ser de este carrito
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado en tu carrito")

    item.cantidad = datos.cantidad
    db.commit()
    db.refresh(carrito)

    respuesta = CarritoRespuesta.model_validate(carrito)
    respuesta.total = calcular_total(carrito)
    return respuesta


# DELETE /carrito/items/{item_id} — eliminar un producto del carrito
@router.delete("/items/{item_id}", response_model=CarritoRespuesta)
def eliminar_item(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_actual)
):
    carrito = get_or_create_carrito(usuario.id, db)

    item = db.query(CarritoItem).filter(
        CarritoItem.id == item_id,
        CarritoItem.carrito_id == carrito.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado en tu carrito")

    db.delete(item)
    db.commit()
    db.refresh(carrito)

    respuesta = CarritoRespuesta.model_validate(carrito)
    respuesta.total = calcular_total(carrito)
    return respuesta


# DELETE /carrito — vaciar el carrito completo
@router.delete("/", response_model=CarritoRespuesta)
def vaciar_carrito(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_actual)
):
    carrito = get_or_create_carrito(usuario.id, db)

    # cascade="all, delete-orphan" en el modelo se encarga de borrar los items
    for item in carrito.items:
        db.delete(item)

    db.commit()
    db.refresh(carrito)

    respuesta = CarritoRespuesta.model_validate(carrito)
    respuesta.total = 0.0
    return respuesta
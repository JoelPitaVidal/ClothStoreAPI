
from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()

productos = [
    {"id": 1, "nombre": "Camiseta", "precio": 19.99, "categoria": "ropa", "stock": 50},
    {"id": 2, "nombre": "Zapatillas", "precio": 89.99, "categoria": "calzado", "stock": 20},
    {"id": 3, "nombre": "Mochila", "precio": 45.00, "categoria": "accesorios", "stock": 15},
    {"id": 4, "nombre": "Pantalón", "precio": 39.99, "categoria": "ropa", "stock": 30},
    {"id": 5, "nombre": "Cinturón", "precio": 14.99, "categoria": "accesorios", "stock": 0},
]

@app.get("/")
def raiz():
    return {"mensaje": "Hola desde FastAPI"}

@app.get("/productos")
def listar_productos(categoria: Optional[str] = None, solo_disponibles: bool = False):
    resultado = productos

    if categoria:
        resultado = [p for p in resultado if p["categoria"] == categoria]

    if solo_disponibles:
        resultado = [p for p in resultado if p["stock"] > 0]

    return resultado

@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: int):
    for producto in productos:
        if producto["id"] == producto_id:
            return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")
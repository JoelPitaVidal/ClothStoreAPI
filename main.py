import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
# 1. Importamos la base de datos y el motor
from database.database import engine, Base

# 2. IMPORTANTE: Importa los modelos de SQLAlchemy (los que tienen __tablename__)
# Si tu archivo se llama 'models.py' y está en la carpeta 'database', sería:
import models
# O si está en la raíz: import models

# 3. Importación de los routers
from routers import productos, categorias, auth, carrito, pedidos, admin, pagos, newsletter


load_dotenv()
# --- CREACIÓN DE TABLAS ---
# Esto ahora sí funcionará porque 'models' ya está cargado en memoria
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tienda API", version="1.1")

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTRO DE RUTAS ---
app.include_router(auth.router, prefix="/auth")
app.include_router(admin.router)
app.include_router(productos.router)
app.include_router(categorias.router)
app.include_router(carrito.router)
app.include_router(pedidos.router)
app.include_router(pagos.router)
app.include_router(newsletter.router)

@app.get("/")
def raiz():
    return {"mensaje": "Tienda API activa", "version": "1.1"}

# --- BLOQUE DE ARRANQUE ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
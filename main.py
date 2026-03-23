# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import productos, categorias

app = FastAPI(title="Tienda API", version="1.0")

# CORS — imprescindible para que Vue pueda conectarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puerto por defecto de Vite+Vue
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(productos.router)
app.include_router(categorias.router)

@app.get("/")
def raiz():
    return {"mensaje": "Tienda API activa", "version": "1.0"}
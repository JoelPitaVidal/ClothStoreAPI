# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import productos, categorias, auth
from database.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tienda API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(categorias.router)

@app.get("/")
def raiz():
    return {"mensaje": "Tienda API activa", "version": "1.0"}
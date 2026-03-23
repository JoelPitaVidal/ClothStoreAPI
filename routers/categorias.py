# routers/categorias.py
from fastapi import APIRouter, HTTPException
from models import CategoriaCrear, CategoriaRespuesta

router = APIRouter(prefix="/categorias", tags=["Categorías"])

categorias = [
    {"id": 1, "nombre": "Ropa", "descripcion": "Camisetas, pantalones, etc."},
    {"id": 2, "nombre": "Calzado", "descripcion": "Zapatos y zapatillas"},
    {"id": 3, "nombre": "Accesorios", "descripcion": "Cinturones, mochilas, etc."},
]
contador_id = len(categorias)


@router.get("/", response_model=list[CategoriaRespuesta])
def listar_categorias():
    return categorias


@router.get("/{categoria_id}", response_model=CategoriaRespuesta)
def obtener_categoria(categoria_id: int):
    for cat in categorias:
        if cat["id"] == categoria_id:
            return cat
    raise HTTPException(status_code=404, detail="Categoría no encontrada")


@router.post("/", response_model=CategoriaRespuesta, status_code=201)
def crear_categoria(categoria: CategoriaCrear):
    global contador_id
    contador_id += 1
    nueva = {"id": contador_id, **categoria.model_dump()}
    categorias.append(nueva)
    return nueva
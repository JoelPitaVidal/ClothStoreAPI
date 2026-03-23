# routers/categorias.py
from fastapi import APIRouter, HTTPException
from models import CategoriaCrear, CategoriaRespuesta

# APIRouter agrupa los endpoints de este recurso.
# prefix="/categorias" → todas las rutas de este archivo empiezan por /categorias
# tags=["Categorías"]  → agrupa los endpoints bajo esa etiqueta en /docs
router = APIRouter(prefix="/categorias", tags=["Categorías"])

# Base de datos temporal en memoria.
# Estos datos se pierden al reiniciar el servidor — se sustituirá por SQLAlchemy más adelante.
categorias = [
    {"id": 1, "nombre": "Ropa", "descripcion": "Camisetas, pantalones, etc."},
    {"id": 2, "nombre": "Calzado", "descripcion": "Zapatos y zapatillas"},
    {"id": 3, "nombre": "Accesorios", "descripcion": "Cinturones, mochilas, etc."},
]

# Contador para simular el autoincremento de ids que haría una base de datos real.
contador_id = len(categorias)


# GET /categorias
# Devuelve la lista completa de categorías.
# response_model valida y filtra la respuesta según CategoriaRespuesta.
@router.get("/", response_model=list[CategoriaRespuesta])
def listar_categorias():
    return categorias


# GET /categorias/{categoria_id}
# Busca una categoría por su id. Si no existe, devuelve un error 404.
@router.get("/{categoria_id}", response_model=CategoriaRespuesta)
def obtener_categoria(categoria_id: int):
    for cat in categorias:
        if cat["id"] == categoria_id:
            return cat
    # HTTPException corta la ejecución y devuelve la respuesta de error inmediatamente
    raise HTTPException(status_code=404, detail="Categoría no encontrada")


# POST /categorias
# Crea una nueva categoría con los datos recibidos en el cuerpo de la petición.
# status_code=201 indica que se ha creado un recurso nuevo (en lugar del 200 por defecto).
@router.post("/", response_model=CategoriaRespuesta, status_code=201)
def crear_categoria(categoria: CategoriaCrear):
    global contador_id  # Necesario para modificar la variable definida fuera de la función
    contador_id += 1

    # ** desempaqueta el diccionario de Pydantic y lo combina con el id generado.
    # Es equivalente a escribir todos los campos a mano pero más limpio.
    nueva = {"id": contador_id, **categoria.model_dump()}
    categorias.append(nueva)
    return nueva


# PUT /categorias/{categoria_id}
# Reemplaza una categoría entera. El cliente debe enviar TODOS los campos.
# A diferencia de PATCH, no permite actualizaciones parciales.
@router.put("/{categoria_id}", response_model=CategoriaRespuesta)
def actualizar_categoria(categoria_id: int, datos: CategoriaCrear):
    for i, c in enumerate(categorias):  # enumerate da el índice (i) y el valor (c) a la vez
        if c["id"] == categoria_id:
            categorias[i] = {"id": categoria_id, **datos.model_dump()}
            return categorias[i]
    raise HTTPException(status_code=404, detail="Categoría no encontrada")


# DELETE /categorias/{categoria_id}
# Elimina una categoría por su id.
# status_code=204 significa "éxito sin contenido" — no se devuelve nada en el body.
@router.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(categoria_id: int):
    for i, c in enumerate(categorias):
        if c["id"] == categoria_id:
            categorias.pop(i)  # pop(i) elimina el elemento en la posición i de la lista
            return
    raise HTTPException(status_code=404, detail="Categoría no encontrada")
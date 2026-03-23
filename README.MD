# 🛍️ Tienda API

API RESTful para una tienda de ropa, construida con **FastAPI** y diseñada para integrarse con un frontend en **Vue.js**. El proyecto está estructurado para crecer — preparado para conectar una base de datos y evolucionar hacia un backend completo en producción.

---

## 🚀 Tecnologías

- **Python 3.10+**
- **FastAPI** — framework moderno y rápido para construir APIs
- **Pydantic v2** — validación y serialización de datos
- **Uvicorn** — servidor ASGI
- **CORS** configurado para Vue + Vite (`localhost:5173`)

---

## 📁 Estructura del proyecto

```
tienda-api/
├── main.py               # Punto de entrada, configuración CORS y registro de routers
├── models.py             # Esquemas Pydantic (modelos de entrada y respuesta)
├── routers/
│   ├── __init__.py
│   ├── productos.py      # Endpoints de productos
│   └── categorias.py     # Endpoints de categorías
└── requirements.txt
```

---

## ⚙️ Instalación y arranque

```bash
# 1. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 2. Instalar dependencias
pip install fastapi uvicorn[standard]

# 3. Arrancar el servidor de desarrollo
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`

Documentación interactiva (Swagger UI) en `http://127.0.0.1:8000/docs`

---

## 📦 Endpoints

### Productos `/productos`

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/productos` | Lista todos los productos. Admite filtros `?categoria_id=` y `?solo_disponibles=true` |
| `GET` | `/productos/{id}` | Obtiene un producto concreto por su ID |
| `POST` | `/productos` | Crea un producto nuevo |
| `PUT` | `/productos/{id}` | Reemplaza un producto completo |
| `PATCH` | `/productos/{id}/stock` | Actualiza el stock (positivo para añadir, negativo para restar) |
| `DELETE` | `/productos/{id}` | Elimina un producto |

#### POST /productos — Cuerpo de la petición
```json
{
  "nombre": "Camiseta",
  "precio": 19.99,
  "stock": 50,
  "categoria_id": 1
}
```

#### PATCH /productos/{id}/stock — Cuerpo de la petición
```json
{
  "cantidad": 10
}
```

---

### Categorías `/categorias`

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/categorias` | Lista todas las categorías |
| `GET` | `/categorias/{id}` | Obtiene una categoría concreta por su ID |
| `POST` | `/categorias` | Crea una categoría nueva |
| `PUT` | `/categorias/{id}` | Reemplaza una categoría completa |
| `DELETE` | `/categorias/{id}` | Elimina una categoría |

#### POST /categorias — Cuerpo de la petición
```json
{
  "nombre": "Ropa",
  "descripcion": "Camisetas, pantalones, etc."
}
```

---

## 🔒 CORS

El CORS está preconfigurado para permitir peticiones desde el servidor de desarrollo de Vue + Vite:

```python
allow_origins=["http://localhost:5173"]
```


---

## 🗂️ Modelos de datos

### ProductoCrear
| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `nombre` | `str` | mínimo 2, máximo 100 caracteres |
| `precio` | `float` | debe ser > 0 |
| `stock` | `int` | debe ser ≥ 0, por defecto 0 |
| `categoria_id` | `int` | debe corresponder a una categoría existente |

### CategoriaCrear
| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `nombre` | `str` | mínimo 2, máximo 50 caracteres |
| `descripcion` | `str` | opcional |

---

## 🔮 Próximos pasos

- [ ] Conectar base de datos SQLite con SQLAlchemy
- [ ] Añadir migraciones con Alembic
- [ ] Añadir campo de URL de imagen en productos
- [ ] Autenticación de usuarios con JWT
- [ ] Rutas protegidas solo para administradores
- [ ] Despliegue en un proveedor cloud (Railway, Render, etc.)

---

## 🤝 Integración con Vue

Conexion la API así:

```javascript
// Ejemplo: obtener todos los productos disponibles de la categoría 1
const response = await fetch('http://127.0.0.1:8000/productos?categoria_id=1&solo_disponibles=true')
const productos = await response.json()
```


---

## 📄 Licencia

MIT
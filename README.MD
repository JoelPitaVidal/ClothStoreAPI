# 🛍️ Tienda API

API RESTful para una tienda de ropa, construida con **FastAPI** y diseñada para integrarse con un frontend en **Vue.js**. Incluye base de datos persistente con SQLite, migraciones con Alembic y estructura modular lista para crecer.

---

## 🚀 Tecnologías

- **Python 3.10+**
- **FastAPI** — framework moderno y rápido para construir APIs
- **Pydantic v2** — validación y serialización de datos
- **SQLAlchemy** — ORM para gestión de la base de datos
- **SQLite** — base de datos local, sin servidor externo
- **Alembic** — migraciones del esquema de base de datos
- **Uvicorn** — servidor ASGI
- **CORS** configurado para Vue + Vite (`localhost:5173`)

---

## 📁 Estructura del proyecto

```
tienda-api/
├── main.py                   # Punto de entrada, CORS y registro de routers
├── models.py                 # Esquemas Pydantic (modelos de entrada y respuesta)
├── database/
│   ├── __init__.py
│   ├── database.py           # Conexión, engine, sesión y get_db
│   └── db_models.py          # Modelos SQLAlchemy (tablas de la base de datos)
├── routers/
│   ├── __init__.py
│   ├── productos.py          # Endpoints de productos
│   └── categorias.py         # Endpoints de categorías
├── alembic/
│   ├── env.py                # Configuración de migraciones
│   └── versions/             # Archivos de migración generados
├── alembic.ini               # Configuración general de Alembic
├── tienda.db                 # Base de datos SQLite (se genera automáticamente)
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
pip install fastapi uvicorn[standard] sqlalchemy alembic

# 3. Aplicar migraciones (crea las tablas en la base de datos)
alembic upgrade head

# 4. Arrancar el servidor de desarrollo
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`

Documentación interactiva (Swagger UI) en `http://127.0.0.1:8000/docs`

---

## 🗃️ Base de datos

La API usa **SQLite** como base de datos. El archivo `tienda.db` se genera automáticamente en la raíz del proyecto al aplicar las migraciones.

Las migraciones se gestionan con **Alembic**. Cada vez que se modifica el esquema (añadir columnas, cambiar tipos, etc.) el flujo es:

```bash
# 1. Modificar el modelo en database/db_models.py
# 2. Generar la migración automáticamente
alembic revision --autogenerate -m "descripcion del cambio"

# 3. Revisar el archivo generado en alembic/versions/
# 4. Aplicar la migración
alembic upgrade head
```

Otros comandos útiles:

```bash
alembic history          # Ver el historial de migraciones
alembic downgrade -1     # Revertir la última migración
alembic current          # Ver en qué migración está la base de datos ahora
```

> **Nota:** el archivo `tienda.db` no debe subirse a Git. Añádelo a `.gitignore`.

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

Si tu aplicación Vue corre en un puerto diferente, actualiza este valor en `main.py`. Al pasar a producción, reemplaza `localhost:5173` por la URL de tu frontend desplegado.

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

## 🤝 Integración con Vue

Desde tu aplicación Vue puedes consumir la API así:

```javascript
// Obtener todos los productos disponibles de la categoría 1
const response = await fetch('http://127.0.0.1:8000/productos?categoria_id=1&solo_disponibles=true')
const productos = await response.json()

// Crear un producto nuevo
const response = await fetch('http://127.0.0.1:8000/productos', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ nombre: 'Camiseta', precio: 19.99, stock: 50, categoria_id: 1 })
})
const nuevo = await response.json()
```

---

## 🔮 Próximos pasos

- [x] Conectar base de datos SQLite con SQLAlchemy
- [x] Añadir migraciones con Alembic
- [ ] Añadir campo de URL de imagen en productos
- [ ] Autenticación de usuarios con JWT
- [ ] Rutas protegidas solo para administradores
- [ ] Despliegue en un proveedor cloud (Railway, Render, etc.)

---

## 📄 Licencia

MIT
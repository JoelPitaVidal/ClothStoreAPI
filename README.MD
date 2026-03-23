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
- **python-dotenv** — gestión de variables de entorno
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
├── .env.example              # Plantilla de variables de entorno
├── .gitignore
└── requirements.txt
```

> `tienda.db` y `.env` se generan localmente y no se incluyen en el repositorio.

---

## ⚙️ Instalación y arranque

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd tienda-api

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear el archivo de variables de entorno
cp .env.example .env

# 5. Aplicar migraciones (crea las tablas en la base de datos)
alembic upgrade head

# 6. Arrancar el servidor de desarrollo
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`

Documentación interactiva (Swagger UI) en `http://127.0.0.1:8000/docs`

---

## 🔧 Variables de entorno

Copia `.env.example` a `.env` y ajusta los valores si es necesario:

```env
DATABASE_URL=sqlite:///./tienda.db
APP_TITLE=Tienda API
APP_VERSION=1.0
```

> El archivo `.env` nunca se sube al repositorio. Solo `.env.example` está versionado.

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
  "imagen_url": "https://ejemplo.com/camiseta.jpg",
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
| `imagen_url` | `str` | opcional |
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
  body: JSON.stringify({
    nombre: 'Camiseta',
    precio: 19.99,
    stock: 50,
    imagen_url: 'https://ejemplo.com/camiseta.jpg',
    categoria_id: 1
  })
})
const nuevo = await response.json()
```

---

## 🔮 Próximos pasos

- [x] Conectar base de datos SQLite con SQLAlchemy
- [x] Añadir migraciones con Alembic
- [x] Añadir campo `imagen_url` en productos
- [x] Variables de entorno con `.env`
- [x] Repositorio limpio en GitHub
- [ ] Autenticación de usuarios con JWT
- [ ] Rutas protegidas solo para administradores
- [ ] Despliegue en un proveedor cloud (Railway, Render, etc.)

---

## 📄 Licencia

MIT
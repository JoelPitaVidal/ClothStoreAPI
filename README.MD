# 🛍️ Tienda API

API RESTful para una tienda de ropa, construida con **FastAPI** y diseñada para integrarse con un frontend en **Vue.js**. Incluye autenticación JWT, carrito de compra, pedidos, gestión de imágenes con Cloudinary, paginación y búsqueda.

---

## 🚀 Tecnologías

- **Python 3.10+**
- **FastAPI** — framework moderno y rápido para construir APIs
- **Pydantic v2** — validación y serialización de datos
- **SQLAlchemy** — ORM para gestión de la base de datos
- **SQLite** — base de datos local, sin servidor externo
- **Alembic** — migraciones del esquema de base de datos
- **python-jose** — generación y verificación de tokens JWT
- **bcrypt** — hashing seguro de contraseñas
- **Cloudinary** — almacenamiento y CDN de imágenes
- **python-dotenv** — gestión de variables de entorno
- **Uvicorn** — servidor ASGI
- **CORS** configurado para Vue + Vite (`localhost:5173`)

---

## 📁 Estructura del proyecto

```
tienda-api/
├── main.py                   # Punto de entrada, CORS y registro de routers
├── models.py                 # Esquemas Pydantic (modelos de entrada y respuesta)
├── auth/
│   ├── __init__.py
│   └── security.py           # JWT, hashing de contraseñas y dependencias de auth
├── database/
│   ├── __init__.py
│   ├── database.py           # Conexión, engine, sesión y get_db
│   └── db_models.py          # Modelos SQLAlchemy (tablas de la base de datos)
├── routers/
│   ├── __init__.py
│   ├── auth.py               # Registro, login, perfil y cambio de contraseña
│   ├── productos.py          # CRUD de productos + subida de imágenes
│   ├── categorias.py         # CRUD de categorías
│   ├── carrito.py            # Carrito de compra persistente
│   └── pedidos.py            # Creación y gestión de pedidos
├── services/
│   ├── __init__.py
│   └── cloudinary_service.py # Subida y eliminación de imágenes en Cloudinary
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── .env.example
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
# Edita .env con tus credenciales

# 5. Aplicar migraciones
alembic upgrade head

# 6. Arrancar el servidor de desarrollo
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`

Documentación interactiva (Swagger UI) en `http://127.0.0.1:8000/docs`

---

## 🔧 Variables de entorno

Copia `.env.example` a `.env` y rellena los valores:

```env
DATABASE_URL=sqlite:///./tienda.db
APP_TITLE=Tienda API
APP_VERSION=1.0
SECRET_KEY=una-clave-secreta-larga-y-aleatoria-minimo-32-caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=30
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
```

> Nunca subas `.env` al repositorio. Solo `.env.example` está versionado.

---

## 🗃️ Base de datos

```bash
# Generar migración tras modificar un modelo
alembic revision --autogenerate -m "descripcion del cambio"

# Aplicar migraciones pendientes
alembic upgrade head

# Otros comandos
alembic history       # historial de migraciones
alembic downgrade -1  # revertir la última migración
alembic current       # migración activa
```

---

## 📦 Endpoints

### Autenticación `/auth`

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| `POST` | `/auth/registro` | Registra un nuevo usuario | Público |
| `POST` | `/auth/login` | Devuelve un token JWT | Público |
| `GET` | `/auth/me` | Perfil del usuario autenticado | Autenticado |
| `PUT` | `/auth/perfil` | Editar nombre y email | Autenticado |
| `PUT` | `/auth/password` | Cambiar contraseña | Autenticado |

#### POST /auth/registro
```json
{
  "nombre": "Ana García",
  "email": "ana@ejemplo.com",
  "password": "mipassword123"
}
```

#### POST /auth/login
```json
{
  "username": "ana@ejemplo.com",
  "password": "mipassword123"
}
```
Respuesta:
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

---

### Productos `/productos`

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| `GET` | `/productos` | Lista con paginación, filtros y búsqueda | Público |
| `GET` | `/productos/{id}` | Detalle de un producto | Público |
| `POST` | `/productos` | Crear producto | Admin |
| `PUT` | `/productos/{id}` | Reemplazar producto | Admin |
| `PATCH` | `/productos/{id}/stock` | Actualizar stock | Admin |
| `DELETE` | `/productos/{id}` | Eliminar producto | Admin |
| `POST` | `/productos/{id}/imagen` | Subir imagen a Cloudinary | Admin |

#### GET /productos — Parámetros

| Parámetro | Tipo | Descripción | Por defecto |
|-----------|------|-------------|-------------|
| `skip` | `int` | Registros a saltar | 0 |
| `limit` | `int` | Máximo de resultados | 10 |
| `busqueda` | `str` | Filtra por nombre | — |
| `categoria_id` | `int` | Filtra por categoría | — |
| `solo_disponibles` | `bool` | Solo con stock > 0 | false |

#### GET /productos — Respuesta
```json
{
  "total": 23,
  "skip": 0,
  "limit": 10,
  "resultados": [...]
}
```

---

### Categorías `/categorias`

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| `GET` | `/categorias` | Lista todas las categorías | Público |
| `GET` | `/categorias/{id}` | Detalle de una categoría | Público |
| `POST` | `/categorias` | Crear categoría | Admin |
| `PUT` | `/categorias/{id}` | Reemplazar categoría | Admin |
| `DELETE` | `/categorias/{id}` | Eliminar categoría | Admin |

---

### Carrito `/carrito`

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| `GET` | `/carrito` | Ver carrito del usuario | Autenticado |
| `POST` | `/carrito/items` | Añadir producto al carrito | Autenticado |
| `PATCH` | `/carrito/items/{item_id}` | Cambiar cantidad de un item | Autenticado |
| `DELETE` | `/carrito/items/{item_id}` | Eliminar un item | Autenticado |
| `DELETE` | `/carrito` | Vaciar el carrito | Autenticado |

#### POST /carrito/items
```json
{
  "producto_id": 1,
  "cantidad": 2
}
```

---

### Pedidos `/pedidos`

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| `POST` | `/pedidos` | Confirmar carrito y crear pedido | Autenticado |
| `GET` | `/pedidos` | Historial de pedidos del usuario | Autenticado |
| `GET` | `/pedidos/{id}` | Detalle de un pedido | Autenticado |
| `GET` | `/pedidos/admin/todos` | Todos los pedidos | Admin |
| `PATCH` | `/pedidos/{id}/estado` | Cambiar estado del pedido | Admin |

#### Estados de un pedido
`pendiente` → `pagado` → `enviado` → `entregado` / `cancelado`

#### PATCH /pedidos/{id}/estado
```json
{
  "estado": "pagado"
}
```

---

## 🔒 Autenticación

La API usa **JWT**. Para acceder a endpoints protegidos incluye el token en la cabecera:

```
Authorization: Bearer <tu_token>
```

Desde Vue:
```javascript
const response = await fetch('http://127.0.0.1:8000/carrito', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

Los tokens expiran según `ACCESS_TOKEN_EXPIRE_MINUTES` en `.env` (por defecto 30 minutos).

---

## 🖼️ Imágenes

Las imágenes se almacenan en **Cloudinary**. El campo `imagen_url` de cada producto contiene la URL pública permanente.

Flujo de subida (solo admin):
1. `POST /productos/{id}/imagen` con el archivo como `multipart/form-data`
2. La API sube la imagen a Cloudinary y guarda la URL en la base de datos
3. La URL está disponible en `GET /productos` para todos los usuarios

---

## 🔒 CORS

Preconfigurado para Vue + Vite en desarrollo:

```python
allow_origins=["http://localhost:5173"]
```

Actualiza este valor en `main.py` al pasar a producción.

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

### UsuarioRegistro
| Campo | Tipo | Restricciones |
|-------|------|---------------|
| `nombre` | `str` | mínimo 2, máximo 50 caracteres |
| `email` | `str` | mínimo 5 caracteres, debe ser único |
| `password` | `str` | mínimo 6 caracteres |

---

## 🔮 Próximos pasos

- [x] CRUD completo de productos y categorías
- [x] Base de datos persistente con SQLAlchemy + Alembic
- [x] Autenticación JWT con roles (admin / usuario)
- [x] Paginación y búsqueda en productos
- [x] Carrito de compra persistente por usuario
- [x] Pedidos con estados y control de stock
- [x] Imágenes con Cloudinary
- [x] Perfil de usuario (editar nombre, email y contraseña)
- [x] Variables de entorno y repositorio limpio en GitHub
- [ ] Conectar con frontend Vue.js
- [ ] Despliegue en un proveedor cloud (Railway, Render, etc.)

---

## 📄 Licencia

MIT
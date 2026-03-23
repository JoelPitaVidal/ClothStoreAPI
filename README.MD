# 🛍️ Tienda API

A RESTful API for a clothing store, built with **FastAPI** and designed to integrate seamlessly with a **Vue.js** frontend. This project is structured for scalability — ready to plug in a database and grow into a full production backend.

---

## 🚀 Tech Stack

- **Python 3.10+**
- **FastAPI** — modern, fast web framework for building APIs
- **Pydantic v2** — data validation and serialization
- **Uvicorn** — ASGI server
- **CORS** configured for Vue + Vite (`localhost:5173`)

---

## 📁 Project Structure

```
tienda-api/
├── main.py               # App entry point, CORS config, router registration
├── models.py             # Pydantic schemas (request & response models)
├── routers/
│   ├── __init__.py
│   ├── productos.py      # Product endpoints
│   └── categorias.py     # Category endpoints
└── requirements.txt
```

---

## ⚙️ Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install fastapi uvicorn[standard]

# 3. Run the development server
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

Interactive docs (Swagger UI) at `http://127.0.0.1:8000/docs`

---

## 📦 Endpoints

### Products `/productos`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/productos` | List all products. Supports `?categoria_id=` and `?solo_disponibles=true` filters |
| `GET` | `/productos/{id}` | Get a single product by ID |
| `POST` | `/productos` | Create a new product |
| `PATCH` | `/productos/{id}/stock` | Update stock (positive to add, negative to subtract) |

#### POST /productos — Request body
```json
{
  "nombre": "Camiseta",
  "precio": 19.99,
  "stock": 50,
  "categoria_id": 1
}
```

#### PATCH /productos/{id}/stock — Request body
```json
{
  "cantidad": 10
}
```

---

### Categories `/categorias`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/categorias` | List all categories |
| `GET` | `/categorias/{id}` | Get a single category by ID |
| `POST` | `/categorias` | Create a new category |

#### POST /categorias — Request body
```json
{
  "nombre": "Ropa",
  "descripcion": "Camisetas, pantalones, etc."
}
```

---

## 🔒 CORS

CORS is pre-configured to allow requests from the Vue + Vite dev server:

```python
allow_origins=["http://localhost:5173"]
```

If your Vue app runs on a different port, update this value in `main.py`.

---

## 🗂️ Data Models

### ProductoCrear
| Field | Type | Constraints |
|-------|------|-------------|
| `nombre` | `str` | min 2, max 100 chars |
| `precio` | `float` | must be > 0 |
| `stock` | `int` | must be ≥ 0, defaults to 0 |
| `categoria_id` | `int` | must match an existing category |

### CategoriaCrear
| Field | Type | Constraints |
|-------|------|-------------|
| `nombre` | `str` | min 2, max 50 chars |
| `descripcion` | `str` | optional |

---

## 🔮 Roadmap

- [ ] Connect SQLite database with SQLAlchemy
- [ ] Add Alembic migrations
- [ ] Add product image URL field
- [ ] User authentication with JWT
- [ ] Admin-only routes for POST/PATCH endpoints
- [ ] Deploy to a cloud provider (Railway, Render, etc.)

---

## 🤝 Vue Integration

From your Vue app, you can call the API like this:

```javascript
// Example: fetch all available products in category 1
const response = await fetch('http://127.0.0.1:8000/productos?categoria_id=1&solo_disponibles=true')
const productos = await response.json()
```

When moving to production, replace the base URL with your deployed API URL and update the CORS `allow_origins` list accordingly.

---

## 📄 License

MIT
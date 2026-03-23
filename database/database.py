# database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()  # Carga las variables del archivo .env


# SQLite guarda en un archivo local — no necesita servidor externo.
# El archivo se crea automáticamente en la raíz del proyecto.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tienda.db")


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necesario solo para SQLite
)

# Cada petición HTTP usará una sesión independiente para hablar con la DB.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredarán todos los modelos SQLAlchemy.
class Base(DeclarativeBase):
    pass

# Dependencia reutilizable que abre y cierra la sesión automáticamente.
# FastAPI ejecuta el código antes del yield, inyecta db en el endpoint,
# y luego ejecuta el finally tanto si hubo error como si no.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
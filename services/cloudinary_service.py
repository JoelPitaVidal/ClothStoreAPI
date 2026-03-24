# services/cloudinary_service.py
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("dhxpnabw5"),
    api_key=os.getenv("253514125533611"),
    api_secret=os.getenv("p04pTmoYIRgZS4XRX0MHxf8ybVw"),
    secure=True  # siempre URLs con https
)

def subir_imagen(archivo_bytes: bytes, nombre: str) -> str:
    """
    Sube una imagen a Cloudinary y devuelve su URL pública.
    Las imágenes se guardan en la carpeta 'tienda/' dentro de tu cuenta.
    """
    try:
        resultado = cloudinary.uploader.upload(
            archivo_bytes,
            folder="tienda",
            public_id=nombre,        # nombre del archivo en Cloudinary
            overwrite=True,          # si ya existe, lo reemplaza
            resource_type="image"
        )
        return resultado["secure_url"]  # URL pública con https
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")


def eliminar_imagen(url: str) -> None:
    """
    Elimina una imagen de Cloudinary a partir de su URL.
    Extrae el public_id de la URL para hacer la llamada correcta.
    """
    try:
        # La URL tiene esta forma:
        # https://res.cloudinary.com/cloud/image/upload/v123/tienda/nombre.jpg
        # El public_id es: tienda/nombre
        partes = url.split("/upload/")
        if len(partes) < 2:
            return
        public_id = partes[1].split("/", 1)[1]  # elimina el vXXXXXX del principio
        public_id = public_id.rsplit(".", 1)[0]  # elimina la extensión
        cloudinary.uploader.destroy(public_id)
    except Exception:
        pass  # si falla el borrado no interrumpimos la operación principal
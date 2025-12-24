import os
import jwt
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests

# CONFIGURACIÓN DE SEGURIDAD (Variables de Entorno)
# Si no encuentra la variable en Render, usará un valor por defecto (solo para pruebas locales)
SECRET_KEY = os.getenv("SECRET_KEY", "clave_temporal_muy_segura_123")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
ALGORITHM = "HS256"

def verify_google_token(token: str):
    """
    Valida el token recibido del frontend con los servidores de Google.
    """
    try:
        # Verificamos el token contra el Client ID de Google
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        return idinfo
    except Exception as e:
        print(f"Error validando token de Google: {e}")
        return None

def create_access_token(data: dict):
    """
    Crea un JSON Web Token (JWT) propio para nuestra aplicación.
    """
    to_encode = data.copy()
    # El token caducará en 24 horas
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
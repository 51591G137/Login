import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import models, services, database

# Inicializamos la App
app = FastAPI()

# Creamos las tablas en la base de datos automáticamente al arrancar
models.Base.metadata.create_all(bind=database.engine)

# Montamos la carpeta 'static' para que el navegador pueda ver el HTML, CSS y JS
# Si entras a /static/index.html verás tu web
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/auth/google")
async def google_auth(request: Request, db: Session = Depends(database.get_db)):
    """
    Endpoint que recibe el 'credential' de Google desde el frontend.
    """
    # 1. Recibir datos del frontend
    payload = await request.json()
    google_token = payload.get("credential")
    
    if not google_token:
        raise HTTPException(status_code=400, detail="Falta el token de Google")

    # 2. Verificar la identidad con el Servicio
    user_data = services.verify_google_token(google_token)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Token de Google inválido")

    # 3. Lógica de Capa de Datos: Buscar usuario por su email
    email = user_data.get("email")
    user = db.query(models.User).filter(models.User.email == email).first()

    # Si el usuario no existe en nuestra DB, lo registramos
    if not user:
        user = models.User(
            email=email,
            name=user_data.get("name"),
            google_id=user_data.get("sub") # El 'sub' es el ID único de Google
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 4. Crear nuestro propio JWT para que el usuario navegue por nuestra web
    my_jwt = services.create_access_token(data={"sub": user.email})

    return {
        "status": "success",
        "access_token": my_jwt,
        "token_type": "bearer"
    }

# Pequeña ruta para comprobar que el backend está vivo
@app.get("/health")
def health_check():
    return {"status": "ok"}
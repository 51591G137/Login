import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import models, services, database

# Inicializamos la App
app = FastAPI()

# Creamos las tablas en la base de datos automáticamente al arrancar
# NOTA: Si cambias la estructura, borra el archivo sql_app.db para que se regenere
models.Base.metadata.create_all(bind=database.engine)

# Montamos la carpeta 'static'
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/auth/google")
async def google_auth(request: Request, db: Session = Depends(database.get_db)):
    """
    Endpoint que recibe el 'credential' de Google, gestiona la identidad 
    en dos tablas y devuelve un JWT.
    """
    # 1. Recibir datos del frontend
    payload = await request.json()
    google_token = payload.get("credential")
    
    if not google_token:
        raise HTTPException(status_code=400, detail="Falta el token de Google")

    # 2. Verificar la identidad con Google (Capa de Servicio)
    user_data = services.verify_google_token(google_token)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Token de Google inválido")

    # 3. Lógica de Identidad Escalable (Capa de Datos)
    # 3.1. Buscar si ya existe la conexión con este proveedor (Google)
    account = db.query(models.Account).filter(
        models.Account.provider == "google",
        models.Account.provider_id == user_data['sub']
    ).first()

    if not account:
        # 3.2. Si la cuenta no existe, ver si el email ya existe en el perfil de Usuario
        user = db.query(models.User).filter(models.User.email == user_data['email']).first()
        
        if not user:
            # Crear perfil de usuario nuevo (Perfil central)
            user = models.User(
                email=user_data['email'],
                full_name=user_data.get('name'),
                avatar_url=user_data.get('picture')
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 3.3. Crear la conexión de la cuenta con Google para este usuario
        account = models.Account(
            user_id=user.id,
            provider="google",
            provider_id=user_data['sub']
        )
        db.add(account)
        db.commit()
    else:
        # Si la cuenta ya existe, recuperamos el usuario vinculado
        user = account.user

    # 4. Generar JWT propio (Stateless)
    my_jwt = services.create_access_token(data={"sub": user.email})

    return {
        "status": "success",
        "access_token": my_jwt,
        "token_type": "bearer"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
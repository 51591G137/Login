from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de la base de datos. Se creará un archivo llamado 'sql_app.db' en la raíz.
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# El motor de la base de datos
# 'check_same_thread': False es necesario solo para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Sesión para interactuar con la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para los modelos (User, etc.)
Base = declarative_base()

# Función auxiliar para obtener la base de datos en las rutas de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    avatar_url = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relación con sus cuentas (Google, etc.)
    accounts = relationship("Account", back_populates="user")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # Ejemplo: "google"
    provider_id = Column(String, unique=True, nullable=False)  # El 'sub' de Google
    
    # Opcionales para JWT, pero recomendados por escalabilidad
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)

    user = relationship("User", back_populates="accounts")
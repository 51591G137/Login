from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    google_id = Column(String, unique=True, nullable=False)
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
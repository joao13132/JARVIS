# backend/models/database.py

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '../../database/jarvis.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"

    id          = Column(Integer, primary_key=True, index=True)
    nome        = Column(String(100))
    email       = Column(String(150), unique=True, index=True)
    senha_hash  = Column(String(255))
    criado_em   = Column(DateTime, default=datetime.now)

    conversas = relationship("Conversa", back_populates="usuario")
    memorias  = relationship("Memoria", back_populates="usuario")


class Conversa(Base):
    __tablename__ = "conversas"

    id          = Column(Integer, primary_key=True, index=True)
    usuario_id  = Column(Integer, ForeignKey("usuarios.id"))
    role        = Column(String(20))
    conteudo    = Column(Text)
    criado_em   = Column(DateTime, default=datetime.now)

    usuario = relationship("Usuario", back_populates="conversas")


class Memoria(Base):
    __tablename__ = "memorias"

    id          = Column(Integer, primary_key=True, index=True)
    usuario_id  = Column(Integer, ForeignKey("usuarios.id"))
    chave       = Column(String(100))
    valor       = Column(Text)
    criado_em   = Column(DateTime, default=datetime.now)

    usuario = relationship("Usuario", back_populates="memorias")


def criar_tabelas():
    Base.metadata.create_all(bind=engine)


def get_db():
    return SessionLocal()
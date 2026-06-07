# backend/models/database.py

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# cria o banco na pasta do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '../../database/jarvis.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# tabela de conversas
class Conversa(Base):
    __tablename__ = "conversas"

    id        = Column(Integer, primary_key=True, index=True)
    role      = Column(String(20))   # "user" ou "assistant"
    conteudo  = Column(Text)
    criado_em = Column(DateTime, default=datetime.now)

# tabela de memórias importantes
class Memoria(Base):
    __tablename__ = "memorias"

    id        = Column(Integer, primary_key=True, index=True)
    chave     = Column(String(100))  # ex: "nome_usuario"
    valor     = Column(Text)         # ex: "João"
    criado_em = Column(DateTime, default=datetime.now)

def criar_tabelas():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass
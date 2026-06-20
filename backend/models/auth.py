# backend/models/auth.py

import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from .database import SessionLocal, Usuario, criar_tabelas

criar_tabelas()

JWT_SECRET = os.getenv("JWT_SECRET", "jarvis-secret-troque-isso-em-producao")
JWT_ALGORITHM = "HS256"
JWT_EXPIRA_HORAS = 24 * 7


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))


def criar_token(usuario_id: int, email: str) -> str:
    payload = {
        "usuario_id": usuario_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRA_HORAS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verificar_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def cadastrar_usuario(nome: str, email: str, senha: str):
    db = SessionLocal()
    try:
        existe = db.query(Usuario).filter(Usuario.email == email).first()
        if existe:
            return None, "Este email já está cadastrado."

        novo = Usuario(nome=nome, email=email, senha_hash=hash_senha(senha))
        db.add(novo)
        db.commit()
        db.refresh(novo)

        token = criar_token(novo.id, novo.email)
        return {"id": novo.id, "nome": novo.nome, "email": novo.email, "token": token}, None

    except Exception as e:
        return None, str(e)
    finally:
        db.close()


def fazer_login(email: str, senha: str):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == email).first()

        if not usuario:
            return None, "Email ou senha incorretos."

        if not verificar_senha(senha, usuario.senha_hash):
            return None, "Email ou senha incorretos."

        token = criar_token(usuario.id, usuario.email)
        return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email, "token": token}, None

    except Exception as e:
        return None, str(e)
    finally:
        db.close()


def obter_usuario_do_token(token: str):
    payload = verificar_token(token)
    if not payload:
        return None

    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.id == payload["usuario_id"]).first()
        if usuario:
            return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email}
        return None
    finally:
        db.close()
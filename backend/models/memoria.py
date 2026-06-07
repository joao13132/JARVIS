# backend/models/memoria.py

from .database import SessionLocal, Conversa, Memoria, criar_tabelas

criar_tabelas()

def salvar_mensagem(role: str, conteudo: str):
    db = SessionLocal()
    try:
        msg = Conversa(role=role, conteudo=conteudo)
        db.add(msg)
        db.commit()
    finally:
        db.close()

def carregar_historico(limite: int = 20):
    db = SessionLocal()
    try:
        conversas = db.query(Conversa)\
            .order_by(Conversa.criado_em.desc())\
            .limit(limite)\
            .all()
        # retorna em ordem cronológica
        return [{"role": c.role, "content": c.conteudo} for c in reversed(conversas)]
    finally:
        db.close()

def salvar_memoria(chave: str, valor: str):
    db = SessionLocal()
    try:
        # atualiza se já existir
        mem = db.query(Memoria).filter(Memoria.chave == chave).first()
        if mem:
            mem.valor = valor
        else:
            mem = Memoria(chave=chave, valor=valor)
            db.add(mem)
        db.commit()
    finally:
        db.close()

def carregar_memoria(chave: str) -> str | None:
    db = SessionLocal()
    try:
        mem = db.query(Memoria).filter(Memoria.chave == chave).first()
        return mem.valor if mem else None
    finally:
        db.close()

def carregar_todas_memorias() -> dict:
    db = SessionLocal()
    try:
        mems = db.query(Memoria).all()
        return {m.chave: m.valor for m in mems}
    finally:
        db.close()
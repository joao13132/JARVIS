# backend/models/memoria.py

from .database import SessionLocal, Conversa, Memoria, criar_tabelas

criar_tabelas()

def salvar_mensagem(usuario_id: int, role: str, conteudo: str):
    db = SessionLocal()
    try:
        msg = Conversa(usuario_id=usuario_id, role=role, conteudo=conteudo)
        db.add(msg)
        db.commit()
    finally:
        db.close()

def carregar_historico(usuario_id: int, limite: int = 20):
    db = SessionLocal()
    try:
        conversas = db.query(Conversa)\
            .filter(Conversa.usuario_id == usuario_id)\
            .order_by(Conversa.criado_em.desc())\
            .limit(limite)\
            .all()
        return [{"role": c.role, "content": c.conteudo} for c in reversed(conversas)]
    finally:
        db.close()

def salvar_memoria(usuario_id: int, chave: str, valor: str):
    db = SessionLocal()
    try:
        mem = db.query(Memoria).filter(
            Memoria.usuario_id == usuario_id,
            Memoria.chave == chave
        ).first()
        if mem:
            mem.valor = valor
        else:
            mem = Memoria(usuario_id=usuario_id, chave=chave, valor=valor)
            db.add(mem)
        db.commit()
    finally:
        db.close()

def carregar_todas_memorias(usuario_id: int) -> dict:
    db = SessionLocal()
    try:
        mems = db.query(Memoria).filter(Memoria.usuario_id == usuario_id).all()
        return {m.chave: m.valor for m in mems}
    finally:
        db.close()
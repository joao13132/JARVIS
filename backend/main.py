# backend/main.py

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from integrations.comandos import executar_comando
from integrations.email_sender import detectar_email
from integrations.tts import falar, parar_fala
from integrations.agenda import detectar_agenda
from integrations.whatsapp import detectar_whatsapp
from integrations.ia_client import gerar_resposta
from models.memoria import (
    salvar_mensagem,
    carregar_historico,
    salvar_memoria,
    carregar_todas_memorias
)
from models.auth import cadastrar_usuario, fazer_login, obter_usuario_do_token
import os
import requests

load_dotenv()

app = FastAPI(title="Jarvis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """Você é o J.A.R.V.I.S., assistente de inteligência artificial 
do Tony Stark. Responda SEMPRE em português brasileiro, nunca em inglês.
Seja eficiente, inteligente e levemente formal. Seja direto e útil."""


class Comando(BaseModel):
    command: str

class MemoriaInput(BaseModel):
    chave: str
    valor: str

class CadastroInput(BaseModel):
    nome: str
    email: str
    senha: str

class LoginInput(BaseModel):
    email: str
    senha: str


def get_usuario_atual(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")

    token = authorization.replace("Bearer ", "")
    usuario = obter_usuario_do_token(token)

    if not usuario:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    return usuario


# ---- AUTENTICAÇÃO ----

@app.post("/api/cadastro")
def cadastro(body: CadastroInput):
    resultado, erro = cadastrar_usuario(body.nome, body.email, body.senha)
    if erro:
        raise HTTPException(status_code=400, detail=erro)
    return resultado


@app.post("/api/login")
def login(body: LoginInput):
    resultado, erro = fazer_login(body.email, body.senha)
    if erro:
        raise HTTPException(status_code=401, detail=erro)
    return resultado


@app.get("/api/me")
def me(authorization: str = Header(None)):
    usuario = get_usuario_atual(authorization)
    return usuario


# ---- STATUS / CLIMA ----

@app.get("/api/status")
def status():
    return {"status": "Jarvis online"}


@app.get("/api/clima")
def get_clima():
    try:
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            return {"erro": "Chave do clima não configurada"}

        city = os.getenv("WEATHER_CITY", "São Paulo")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=pt_br"
        r = requests.get(url, timeout=5)
        data = r.json()

        if data.get("cod") != 200:
            return {"erro": data.get("message", "erro desconhecido")}

        return {
            "cidade": data["name"],
            "pais": data["sys"]["country"],
            "temp": round(data["main"]["temp"]),
            "sensacao": round(data["main"]["feels_like"]),
            "umidade": data["main"]["humidity"],
            "descricao": data["weather"][0]["description"].upper(),
            "vento": round(data["wind"]["speed"] * 3.6)
        }
    except Exception as e:
        return {"erro": str(e)}


# ---- HISTÓRICO / MEMÓRIA (por usuário) ----

@app.get("/api/historico")
def get_historico(authorization: str = Header(None)):
    usuario = get_usuario_atual(authorization)
    return {"historico": carregar_historico(usuario["id"], 50)}


@app.get("/api/memorias")
def get_memorias(authorization: str = Header(None)):
    usuario = get_usuario_atual(authorization)
    return {"memorias": carregar_todas_memorias(usuario["id"])}


@app.post("/api/memoria")
def salvar_mem(body: MemoriaInput, authorization: str = Header(None)):
    usuario = get_usuario_atual(authorization)
    salvar_memoria(usuario["id"], body.chave, body.valor)
    return {"status": "Memória salva"}


@app.post("/api/parar")
def parar():
    parar_fala()
    return {"status": "fala pausada"}


# ---- COMANDO PRINCIPAL ----

@app.post("/api/command")
def processar_comando(body: Comando, authorization: str = Header(None)):
    usuario = get_usuario_atual(authorization)
    uid = usuario["id"]

    resultado = executar_comando(body.command)
    if resultado:
        salvar_mensagem(uid, "user", body.command)
        salvar_mensagem(uid, "assistant", resultado)
        falar(resultado)
        return {"response": resultado}

    resultado_agenda = detectar_agenda(body.command)
    if resultado_agenda:
        salvar_mensagem(uid, "user", body.command)
        salvar_mensagem(uid, "assistant", resultado_agenda)
        falar(resultado_agenda)
        return {"response": resultado_agenda}

    resultado_email = detectar_email(body.command)
    if resultado_email:
        salvar_mensagem(uid, "user", body.command)
        salvar_mensagem(uid, "assistant", resultado_email)
        falar(resultado_email)
        return {"response": resultado_email}

    resultado_whatsapp = detectar_whatsapp(body.command)
    if resultado_whatsapp:
        salvar_mensagem(uid, "user", body.command)
        salvar_mensagem(uid, "assistant", resultado_whatsapp)
        falar(resultado_whatsapp)
        return {"response": resultado_whatsapp}

    salvar_mensagem(uid, "user", body.command)

    historico = carregar_historico(uid, 20)
    memorias = carregar_todas_memorias(uid)

    contexto = SYSTEM_PROMPT
    contexto += f"\n\nO nome do usuário é {usuario['nome']}."
    if memorias:
        contexto += "\n\nInformações que você lembra do usuário:\n"
        for chave, valor in memorias.items():
            contexto += f"- {chave}: {valor}\n"

    mensagens = [{"role": "system", "content": contexto}] + historico

    texto = gerar_resposta(mensagens)
    salvar_mensagem(uid, "assistant", texto)
    falar(texto)

    return {"response": texto}


app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
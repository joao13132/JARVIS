from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from integrations.comandos import executar_comando
from integrations.email_sender import detectar_email
from models.memoria import (
    salvar_mensagem,
    carregar_historico,
    salvar_memoria,
    carregar_todas_memorias
)
import os

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

app = FastAPI(title="Jarvis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """Você é o J.A.R.V.I.S., assistente de inteligência artificial 
do Tony Stark. Responda sempre em português brasileiro, de forma 
eficiente, inteligente e levemente formal. Seja direto e útil.
Você tem memória persistente e lembra de conversas anteriores."""

class Comando(BaseModel):
    command: str

class MemoriaInput(BaseModel):
    chave: str
    valor: str

@app.get("/api/status")
def status():
    return {"status": "Jarvis online"}

@app.get("/api/historico")
def get_historico():
    return {"historico": carregar_historico(50)}

@app.get("/api/memorias")
def get_memorias():
    return {"memorias": carregar_todas_memorias()}

@app.post("/api/memoria")
def salvar_mem(body: MemoriaInput):
    salvar_memoria(body.chave, body.valor)
    return {"status": "Memória salva"}

@app.post("/api/command")
def processar_comando(body: Comando):
    # 1. tenta comando do sistema
    resultado = executar_comando(body.command)
    if resultado:
        salvar_mensagem("user", body.command)
        salvar_mensagem("assistant", resultado)
        return {"response": resultado}

    # 2. tenta comando de email
    resultado_email = detectar_email(body.command, client, [])
    if resultado_email:
        salvar_mensagem("user", body.command)
        salvar_mensagem("assistant", resultado_email)
        return {"response": resultado_email}

    # 3. manda para a IA com histórico do banco
    salvar_mensagem("user", body.command)

    historico = carregar_historico(20)
    memorias = carregar_todas_memorias()

    # adiciona memórias ao contexto
    contexto = SYSTEM_PROMPT
    if memorias:
        contexto += f"\n\nInformações que você lembra do usuário:\n"
        for chave, valor in memorias.items():
            contexto += f"- {chave}: {valor}\n"

    mensagens = [{"role": "system", "content": contexto}] + historico

    resposta = client.chat.completions.create(
        model="openrouter/auto",
        messages=mensagens
    )

    texto = resposta.choices[0].message.content
    salvar_mensagem("assistant", texto)

    return {"response": texto}

app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
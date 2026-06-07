from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from integrations.comandos import executar_comando
from integrations.email_sender import detectar_email
from integrations.tts import falar, parar_fala
from integrations.agenda import detectar_agenda
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
do Tony Stark. Responda SEMPRE em português brasileiro, nunca em inglês.
Seja eficiente, inteligente e levemente formal. Seja direto e útil."""

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

@app.post("/api/parar")
def parar():
    parar_fala()
    return {"status": "fala pausada"}

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
        falar(resultado)
        return {"response": resultado}

    # 2. tenta comando de agenda
    resultado_agenda = detectar_agenda(body.command, client)
    if resultado_agenda:
        salvar_mensagem("user", body.command)
        salvar_mensagem("assistant", resultado_agenda)
        falar(resultado_agenda)
        return {"response": resultado_agenda}

    # 3. tenta comando de email
    resultado_email = detectar_email(body.command, client, [])
    if resultado_email:
        salvar_mensagem("user", body.command)
        salvar_mensagem("assistant", resultado_email)
        falar(resultado_email)
        return {"response": resultado_email}

    # 4. manda para a IA com histórico do banco
    salvar_mensagem("user", body.command)

    historico = carregar_historico(20)
    memorias = carregar_todas_memorias()

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
    falar(texto)

    return {"response": texto}

app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from integrations.comandos import executar_comando
from integrations.email_sender import detectar_email
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

historico = [
    {
        "role": "system",
        "content": """Você é o J.A.R.V.I.S., assistente de inteligência artificial 
        do Tony Stark. Responda sempre em português brasileiro, de forma 
        eficiente, inteligente e levemente formal. Seja direto e útil."""
    }
]

class Comando(BaseModel):
    command: str

@app.get("/api/status")
def status():
    return {"status": "Jarvis online"}

@app.post("/api/command")
def processar_comando(body: Comando):
    # 1. tenta comando do sistema
    resultado = executar_comando(body.command)
    if resultado:
        return {"response": resultado}

    # 2. tenta comando de email
    resultado_email = detectar_email(body.command, client, historico)
    if resultado_email:
        return {"response": resultado_email}

    # 3. manda para a IA responder
    historico.append({
        "role": "user",
        "content": body.command
    })

    resposta = client.chat.completions.create(
        model="openrouter/auto",
        messages=historico
    )

    texto = resposta.choices[0].message.content

    historico.append({
        "role": "assistant",
        "content": texto
    })

    return {"response": texto}

app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
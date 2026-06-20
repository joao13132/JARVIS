# backend/integrations/ia_client.py

from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODELO_GROQ = "llama-3.3-70b-versatile"


def gerar_resposta(mensagens: list) -> str:
    """Gera resposta usando Groq — extremamente rápido."""
    resposta = groq_client.chat.completions.create(
        model=MODELO_GROQ,
        messages=mensagens,
        temperature=0.7,
        max_tokens=600
    )
    return resposta.choices[0].message.content


def gerar_resposta_json(prompt: str) -> str:
    """Gera resposta em formato JSON para extração de dados (email, agenda, whatsapp)."""
    resposta = groq_client.chat.completions.create(
        model=MODELO_GROQ,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300
    )
    return resposta.choices[0].message.content
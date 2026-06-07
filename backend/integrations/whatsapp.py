# backend/integrations/whatsapp.py

import webbrowser
import urllib.parse
import time
import pyautogui
from openai import OpenAI

def detectar_whatsapp(texto: str, client_ia) -> str | None:
    texto_lower = texto.lower()
    
    # ignora se for comando de email
    if any(p in texto_lower for p in ["email", "e-mail"]):
        return None
    
    palavras = ["whatsapp", "zap", "mensagem para", "mandar mensagem",
                "enviar mensagem", "manda mensagem", "falar com"]

    if not any(p in texto_lower for p in palavras):
        return None

def enviar_whatsapp(numero: str, mensagem: str) -> str:
    try:
        # formata o número removendo espaços e traços
        numero = numero.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        # adiciona código do Brasil se não tiver
        if not numero.startswith("+"):
            if not numero.startswith("55"):
                numero = "55" + numero

        # codifica a mensagem para URL
        mensagem_encoded = urllib.parse.quote(mensagem)

        # abre o WhatsApp Web com a mensagem pronta
        url = f"https://web.whatsapp.com/send?phone={numero}&text={mensagem_encoded}"
        webbrowser.open(url)

        # espera o WhatsApp Web carregar e envia
        time.sleep(8)
        pyautogui.press('enter')

        return f"Mensagem enviada para {numero} no WhatsApp."

    except Exception as e:
        return f"Erro ao enviar WhatsApp: {str(e)}"


def abrir_whatsapp() -> str:
    webbrowser.open("https://web.whatsapp.com")
    return "Abrindo o WhatsApp Web."


def detectar_whatsapp(texto: str, client_ia) -> str | None:
    palavras = ["whatsapp", "zap", "mensagem para", "mandar mensagem",
                "enviar mensagem", "manda mensagem", "falar com"]

    if not any(p in texto.lower() for p in palavras):
        return None

    # só abrir o WhatsApp
    if any(p in texto.lower() for p in ["abrir whatsapp", "abre whatsapp", "abrir zap"]):
        return abrir_whatsapp()

    # extrai número e mensagem via IA
    prompt = f"""O usuário disse: "{texto}"

Extraia as informações e responda APENAS em JSON:
{{
  "numero": "número do telefone com DDD",
  "mensagem": "conteúdo da mensagem"
}}

Se não tiver número, coloque null.
Se não tiver mensagem, coloque null.
Responda APENAS o JSON, sem texto adicional."""

    resposta = client_ia.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        texto_resp = resposta.choices[0].message.content.strip()
        texto_resp = texto_resp.replace("```json", "").replace("```", "").strip()
        dados = json.loads(texto_resp)

        numero = dados.get("numero")
        mensagem = dados.get("mensagem")

        if not numero or numero == "null":
            return "Para quem devo enviar a mensagem? Diga o número com DDD."

        if not mensagem or mensagem == "null":
            return "Qual mensagem devo enviar?"

        return enviar_whatsapp(numero, mensagem)

    except Exception as e:
        return "Não entendi. Tente: 'manda mensagem no WhatsApp para 11999999999 dizendo olá'"
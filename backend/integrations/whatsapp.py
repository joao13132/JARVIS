# backend/integrations/whatsapp.py

import webbrowser
import urllib.parse
import time
import json
from .ia_client import gerar_resposta_json

try:
    import pyautogui
    PYAUTOGUI_OK = True
except Exception:
    PYAUTOGUI_OK = False


def enviar_whatsapp(numero: str, mensagem: str) -> str:
    try:
        numero = numero.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        if not numero.startswith("+"):
            if not numero.startswith("55"):
                numero = "55" + numero

        mensagem_encoded = urllib.parse.quote(mensagem)
        url = f"https://web.whatsapp.com/send?phone={numero}&text={mensagem_encoded}"
        webbrowser.open(url)

        if PYAUTOGUI_OK:
            time.sleep(8)
            pyautogui.press('enter')
            return f"Mensagem enviada para {numero} no WhatsApp."
        else:
            return f"WhatsApp Web aberto para {numero}. Envie a mensagem manualmente."

    except Exception as e:
        return f"Erro ao enviar WhatsApp: {str(e)}"


def abrir_whatsapp() -> str:
    webbrowser.open("https://web.whatsapp.com")
    return "Abrindo o WhatsApp Web."


def detectar_whatsapp(texto: str) -> str | None:
    texto_lower = texto.lower()

    if any(p in texto_lower for p in ["email", "e-mail"]):
        return None

    palavras = ["whatsapp", "zap", "mensagem para", "mandar mensagem",
                "enviar mensagem", "manda mensagem", "falar com"]

    if not any(p in texto_lower for p in palavras):
        return None

    if any(p in texto_lower for p in ["abrir whatsapp", "abre whatsapp", "abrir zap"]):
        return abrir_whatsapp()

    prompt = f"""O usuário disse: "{texto}"

Extraia as informações e responda APENAS em JSON:
{{
  "numero": "número do telefone com DDD",
  "mensagem": "conteúdo da mensagem"
}}

Se não tiver número, coloque null.
Se não tiver mensagem, coloque null.
Responda APENAS o JSON, sem texto adicional."""

    try:
        texto_resp = gerar_resposta_json(prompt).strip()
        texto_resp = texto_resp.replace("```json", "").replace("```", "").strip()
        dados = json.loads(texto_resp)

        numero = dados.get("numero")
        mensagem = dados.get("mensagem")

        if not numero or numero == "null":
            return "Para quem devo enviar a mensagem? Diga o número com DDD."

        if not mensagem or mensagem == "null":
            return "Qual mensagem devo enviar?"

        return enviar_whatsapp(numero, mensagem)

    except Exception:
        return "Não entendi. Tente: 'manda mensagem no WhatsApp para 11999999999 dizendo olá'"
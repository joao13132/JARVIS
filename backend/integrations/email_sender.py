# backend/integrations/email_sender.py

import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def enviar_email(destinatario: str, assunto: str, mensagem: str) -> str:
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        return f"Email enviado para {destinatario} com sucesso."

    except Exception as e:
        return f"Erro ao enviar email: {str(e)}"


def detectar_email(texto: str, client, historico_ia: list) -> str | None:
    texto_lower = texto.lower()

    # ignora se for comando de WhatsApp
    if any(p in texto_lower for p in ["whatsapp", "zap", "wpp"]):
        return None

    # verifica se é comando de email
    palavras_email = ["email", "e-mail"]
    if not any(p in texto_lower for p in palavras_email):
        return None

    # usa a IA para extrair destinatário, assunto e mensagem
    prompt = f"""O usuário disse: "{texto_lower}"
    
Extraia as informações do email e responda APENAS em JSON assim:
{{
  "destinatario": "email@exemplo.com",
  "assunto": "assunto do email",
  "mensagem": "corpo do email"
}}

Se faltar alguma informação, coloque null no campo.
Responda APENAS o JSON, sem texto adicional."""

    resposta = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        texto_resposta = resposta.choices[0].message.content.strip()
        texto_resposta = texto_resposta.replace("```json", "").replace("```", "").strip()
        dados = json.loads(texto_resposta)

        destinatario = dados.get("destinatario")
        assunto = dados.get("assunto")
        mensagem = dados.get("mensagem")

        if not destinatario or destinatario == "null":
            return "Para quem devo enviar o email? Por favor, diga o endereço de email."

        if not assunto or assunto == "null":
            assunto = "Mensagem do Jarvis"

        if not mensagem or mensagem == "null":
            return "Qual mensagem devo enviar no email?"

        return enviar_email(destinatario, assunto, mensagem)

    except Exception as e:
        return f"Não consegui entender os dados do email. Tente: envie um email para fulano@gmail.com com assunto teste dizendo olá."
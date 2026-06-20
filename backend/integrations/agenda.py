# backend/integrations/agenda.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
import pickle
import json
from .ia_client import gerar_resposta_json

SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(os.path.dirname(BASE_DIR), 'credentials.json')
TOKEN_PATH = os.path.join(os.path.dirname(BASE_DIR), 'token.pickle')


def get_service():
    creds = None

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'wb') as f:
            pickle.dump(creds, f)

    return build('calendar', 'v3', credentials=creds)


def criar_evento(titulo: str, data: str, hora: str, duracao: int = 60) -> str:
    try:
        service = get_service()
        dt_str = f"{data} {hora}"
        dt_inicio = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        dt_fim = dt_inicio + timedelta(minutes=duracao)

        evento = {
            'summary': titulo,
            'start': {'dateTime': dt_inicio.isoformat(), 'timeZone': 'America/Sao_Paulo'},
            'end': {'dateTime': dt_fim.isoformat(), 'timeZone': 'America/Sao_Paulo'},
        }

        service.events().insert(calendarId='primary', body=evento).execute()
        return f"Evento '{titulo}' criado para {data} às {hora}."

    except Exception as e:
        return f"Erro ao criar evento: {str(e)}"


def listar_eventos(dias: int = 7) -> str:
    try:
        service = get_service()
        agora = datetime.utcnow().isoformat() + 'Z'
        limite = (datetime.utcnow() + timedelta(days=dias)).isoformat() + 'Z'

        resultado = service.events().list(
            calendarId='primary', timeMin=agora, timeMax=limite,
            maxResults=10, singleEvents=True, orderBy='startTime'
        ).execute()

        eventos = resultado.get('items', [])
        if not eventos:
            return f"Nenhum evento nos próximos {dias} dias."

        resposta = "Seus próximos eventos:\n"
        for e in eventos:
            inicio = e['start'].get('dateTime', e['start'].get('date'))
            try:
                dt = datetime.fromisoformat(inicio.replace('Z', '+00:00'))
                inicio_fmt = dt.strftime("%d/%m às %H:%M")
            except Exception:
                inicio_fmt = inicio
            resposta += f"- {e['summary']} em {inicio_fmt}\n"

        return resposta

    except Exception as e:
        return f"Erro ao listar eventos: {str(e)}"


def deletar_evento(titulo: str) -> str:
    try:
        service = get_service()
        agora = datetime.utcnow().isoformat() + 'Z'
        resultado = service.events().list(
            calendarId='primary', timeMin=agora, maxResults=10,
            singleEvents=True, orderBy='startTime', q=titulo
        ).execute()

        eventos = resultado.get('items', [])
        if not eventos:
            return f"Nenhum evento encontrado com o nome '{titulo}'."

        service.events().delete(calendarId='primary', eventId=eventos[0]['id']).execute()
        return f"Evento '{eventos[0]['summary']}' deletado com sucesso."

    except Exception as e:
        return f"Erro ao deletar evento: {str(e)}"


def detectar_agenda(texto: str) -> str | None:
    palavras = ["agendar", "agenda", "evento", "compromisso", "reunião",
                "marcar", "listar eventos", "próximos eventos", "cancelar evento",
                "deletar evento", "remover evento"]

    if not any(p in texto.lower() for p in palavras):
        return None

    prompt = f"""O usuário disse: "{texto}"

Identifique a intenção e extraia os dados. Responda APENAS em JSON:

Para criar evento:
{{"acao": "criar", "titulo": "nome do evento", "data": "YYYY-MM-DD", "hora": "HH:MM", "duracao": 60}}

Para listar eventos:
{{"acao": "listar", "dias": 7}}

Para deletar evento:
{{"acao": "deletar", "titulo": "nome do evento"}}

Se não tiver data, use a data de hoje: {datetime.now().strftime("%Y-%m-%d")}
Se não tiver hora, use "09:00"
Responda APENAS o JSON, sem texto adicional."""

    try:
        texto_resp = gerar_resposta_json(prompt).strip()
        texto_resp = texto_resp.replace("```json", "").replace("```", "").strip()
        dados = json.loads(texto_resp)

        acao = dados.get("acao")

        if acao == "criar":
            return criar_evento(
                dados.get("titulo", "Evento"),
                dados.get("data", datetime.now().strftime("%Y-%m-%d")),
                dados.get("hora", "09:00"),
                dados.get("duracao", 60)
            )
        elif acao == "listar":
            return listar_eventos(dados.get("dias", 7))
        elif acao == "deletar":
            return deletar_evento(dados.get("titulo", ""))

    except Exception:
        return "Não entendi o comando de agenda. Tente: 'agendar reunião amanhã às 14h'"

    return None
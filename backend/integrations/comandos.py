# backend/integrations/comandos.py

import subprocess
import os
import webbrowser
import psutil
from datetime import datetime

# apps conhecidos com nome amigável -> comando real
APPS_CONHECIDOS = {
    "chrome": "start chrome",
    "navegador": "start chrome",
    "notepad": "notepad",
    "bloco de notas": "notepad",
    "calculadora": "calc",
    "explorador": "explorer",
    "arquivos": "explorer",
    "explorer": "explorer",
    "spotify": "start spotify",
    "vscode": "code",
    "vs code": "code",
    "código": "code",
    "word": "start winword",
    "excel": "start excel",
    "powerpoint": "start powerpnt",
    "youtube": "start chrome https://www.youtube.com",
    "gmail": "start chrome https://mail.google.com",
    "email": "start chrome https://mail.google.com",
    "whatsapp": "start chrome https://web.whatsapp.com",
    "netflix": "start chrome https://www.netflix.com",
    "discord": "start discord",
    "steam": "start steam",
    "telegram": "start telegram",
    "instagram": "start chrome https://www.instagram.com",
    "twitter": "start chrome https://www.twitter.com",
    "x": "start chrome https://www.x.com",
    "github": "start chrome https://www.github.com",
    "drive": "start chrome https://drive.google.com",
    "google drive": "start chrome https://drive.google.com",
    "maps": "start chrome https://maps.google.com",
    "google maps": "start chrome https://maps.google.com",
}


def tentar_abrir_app_generico(nome_app: str) -> bool:
    """Tenta abrir um app pelo nome direto via comando start do Windows."""
    try:
        nome_limpo = nome_app.strip().lower().replace(" ", "")
        subprocess.Popen(f"start {nome_limpo}", shell=True)
        return True
    except Exception:
        return False


def executar_comando(texto: str) -> str:
    texto = texto.lower().strip()

    # ---- ABRIR APLICATIVOS / SITES ----
    if "abrir" in texto or "abre" in texto:
        comando_sem_verbo = texto.replace("abrir", "").replace("abre", "").strip()

        # procura nos apps conhecidos primeiro
        for nome, cmd in APPS_CONHECIDOS.items():
            if nome in texto:
                subprocess.Popen(cmd, shell=True)
                return f"Abrindo {nome.title()}."

        # se não reconheceu, tenta abrir genericamente pelo nome dito
        if comando_sem_verbo:
            sucesso = tentar_abrir_app_generico(comando_sem_verbo)
            if sucesso:
                return f"Tentando abrir {comando_sem_verbo}."
            else:
                return f"Não consegui localizar o aplicativo '{comando_sem_verbo}'. Verifique se está instalado."

    # ---- PESQUISAR NA INTERNET ----
    if "pesquisar" in texto or "pesquise" in texto or "buscar" in texto or "busque" in texto:
        termo = texto.replace("pesquisar", "").replace("pesquise", "").replace("buscar", "").replace("busque", "").strip()
        if termo:
            url = f"https://www.google.com/search?q={termo.replace(' ', '+')}"
            webbrowser.open(url)
            return f"Pesquisando por {termo} no Google."

    if "youtube" in texto and ("pesquisar" in texto or "procurar" in texto or "tocar" in texto):
        termo = texto.replace("youtube", "").replace("pesquisar", "").replace("procurar", "").replace("tocar", "").strip()
        if termo:
            url = f"https://www.youtube.com/results?search_query={termo.replace(' ', '+')}"
            webbrowser.open(url)
            return f"Pesquisando {termo} no YouTube."

    # ---- CRIAR ARQUIVOS ----
    if "criar" in texto or "crie" in texto or "novo" in texto:

        if "arquivo" in texto or "texto" in texto or "txt" in texto:
            nome = f"arquivo_{datetime.now().strftime('%H%M%S')}.txt"
            caminho = os.path.join(os.path.expanduser("~"), "Desktop", nome)
            with open(caminho, "w") as f:
                f.write(f"Arquivo criado pelo Jarvis em {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            return f"Arquivo {nome} criado na área de trabalho."

        if "pasta" in texto or "diretório" in texto:
            nome = f"pasta_{datetime.now().strftime('%H%M%S')}"
            caminho = os.path.join(os.path.expanduser("~"), "Desktop", nome)
            os.makedirs(caminho, exist_ok=True)
            return f"Pasta {nome} criada na área de trabalho."

    # ---- INFORMAÇÕES DO SISTEMA ----
    if "hora" in texto or "horas" in texto:
        agora = datetime.now().strftime("%H:%M")
        return f"São {agora}."

    if "data" in texto:
        hoje = datetime.now().strftime("%d de %B de %Y")
        return f"Hoje é {hoje}."

    if "memória" in texto or "ram" in texto:
        mem = psutil.virtual_memory()
        return f"Uso de memória RAM: {mem.percent}% utilizado de {round(mem.total / (1024**3), 1)} GB."

    if "bateria" in texto:
        bat = psutil.sensors_battery()
        if bat:
            return f"Bateria em {round(bat.percent)}%. {'Carregando.' if bat.power_plugged else 'Desconectado.'}"
        return "Não detectei bateria neste dispositivo."

    if "desligar" in texto or "reiniciar" in texto:
        return "Por segurança, não executo comandos de desligamento. Por favor, faça isso manualmente."

    return None
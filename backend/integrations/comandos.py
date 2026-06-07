# backend/integrations/comandos.py

import subprocess
import os
import webbrowser
import psutil
from datetime import datetime

def executar_comando(texto: str) -> str:
    texto = texto.lower().strip()

    # ---- ABRIR APLICATIVOS ----
    if "abrir" in texto or "abre" in texto:

        if "chrome" in texto or "navegador" in texto:
            subprocess.Popen("start chrome", shell=True)
            return "Abrindo o Google Chrome."

        if "notepad" in texto or "bloco de notas" in texto:
            subprocess.Popen("notepad", shell=True)
            return "Abrindo o Bloco de Notas."

        if "calculadora" in texto:
            subprocess.Popen("calc", shell=True)
            return "Abrindo a Calculadora."

        if "explorador" in texto or "arquivos" in texto or "explorer" in texto:
            subprocess.Popen("explorer", shell=True)
            return "Abrindo o Explorador de Arquivos."

        if "spotify" in texto:
            subprocess.Popen("start spotify", shell=True)
            return "Abrindo o Spotify."

        if "vscode" in texto or "vs code" in texto or "código" in texto:
            subprocess.Popen("code", shell=True)
            return "Abrindo o VS Code."

        if "word" in texto:
            subprocess.Popen("start winword", shell=True)
            return "Abrindo o Microsoft Word."

        if "excel" in texto:
            subprocess.Popen("start excel", shell=True)
            return "Abrindo o Microsoft Excel."

    # ---- PESQUISAR NA INTERNET ----
    if "pesquisar" in texto or "pesquise" in texto or "buscar" in texto or "busque" in texto:
        termo = texto.replace("pesquisar", "").replace("pesquise", "").replace("buscar", "").replace("busque", "").strip()
        if termo:
            url = f"https://www.google.com/search?q={termo.replace(' ', '+')}"
            webbrowser.open(url)
            return f"Pesquisando por {termo} no Google."

    if "youtube" in texto:
        termo = texto.replace("youtube", "").replace("abrir", "").replace("pesquisar", "").strip()
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

    # nenhum comando detectado
    return None
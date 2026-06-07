# backend/integrations/tts.py

from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import tempfile
import os
import threading
import subprocess

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

try:
    import pygame
    pygame.mixer.init()
    PYGAME_OK = True
except Exception:
    PYGAME_OK = False

_processo_powershell = None

def parar_fala():
    global _processo_powershell
    try:
        if PYGAME_OK:
            pygame.mixer.music.stop()
    except Exception:
        pass
    try:
        if _processo_powershell:
            _processo_powershell.terminate()
            _processo_powershell = None
    except Exception:
        pass
    try:
        subprocess.Popen(
            ["powershell", "-Command", "Stop-Process -Name powershell -ErrorAction SilentlyContinue"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

def falar_browser(texto: str):
    global _processo_powershell
    texto_escaped = texto.replace("'", "")
    script = f"Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = -2; $s.Speak('{texto_escaped}')"
    try:
        _processo_powershell = subprocess.Popen(["powershell", "-Command", script])
    except Exception as e:
        print(f"Erro PowerShell: {e}")

def falar(texto: str):
    def _falar():
        try:
            audio = client.text_to_speech.convert(
                voice_id=VOICE_ID,
                text=texto,
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.75,
                    "similarity_boost": 0.85,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            )

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                for chunk in audio:
                    f.write(chunk)
                caminho = f.name

            if PYGAME_OK:
                pygame.mixer.music.load(caminho)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

            try:
                os.unlink(caminho)
            except Exception:
                pass

        except Exception as e:
            print(f"Erro ElevenLabs: {e}")
            falar_browser(texto)

    thread = threading.Thread(target=_falar)
    thread.daemon = True
    thread.start()
# backend/integrations/tts.py

from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from playsound import playsound
import tempfile
import os
import threading

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

def falar(texto: str):
    def _falar():
        try:
            audio = client.text_to_speech.convert(
    voice_id=VOICE_ID,
    text=texto,
    model_id="eleven_multilingual_v2",)

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                for chunk in audio:
                    f.write(chunk)
                caminho = f.name

            playsound(caminho)
            os.unlink(caminho)

        except Exception as e:
            print(f"Erro ElevenLabs: {e}")

    thread = threading.Thread(target=_falar)
    thread.daemon = True
    thread.start()
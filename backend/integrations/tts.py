# backend/integrations/tts.py

from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import tempfile
import os
import threading

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

import pygame
pygame.mixer.init()

def parar_fala():
    try:
        pygame.mixer.music.stop()
    except:
        pass

def falar(texto: str):
    def _falar():
        try:
            parar_fala()

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

            pygame.mixer.music.load(caminho)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            try:
                os.unlink(caminho)
            except:
                pass

        except Exception as e:
            print(f"Erro ElevenLabs: {e}")

    thread = threading.Thread(target=_falar)
    thread.daemon = True
    thread.start()
// js/main.js — Lógica principal: voz, estados visuais, teclado

const coreCenter = document.getElementById('coreCenter');
const coreOrb    = document.getElementById('coreOrb');
const coreLabel  = document.getElementById('coreLabel');
const status     = document.getElementById('statusBar');
const transcript = document.getElementById('transcript-display');

let isListening = false;
let recognition = null;
let processando = false;

// ---- controle de estado visual central ----
function setMode(mode, label) {
  window.jarvisState.mode = mode;
  coreOrb.classList.remove('listening', 'thinking', 'speaking');
  if (mode !== 'idle') coreOrb.classList.add(mode);
  if (label) coreLabel.textContent = label;
}

// ---- análise de áudio do microfone (reatividade visual) ----
let audioCtx, analyser, micSource, micStream;

async function iniciarAnaliseAudio() {
  try {
    micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    micSource = audioCtx.createMediaStreamSource(micStream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    micSource.connect(analyser);
    medirVolume();
  } catch (e) {
    console.log('Microfone não disponível para análise visual:', e);
  }
}

function medirVolume() {
  if (!analyser) return;
  const data = new Uint8Array(analyser.frequencyBinCount);
  analyser.getByteFrequencyData(data);
  const avg = data.reduce((a, b) => a + b, 0) / data.length;
  window.jarvisState.audioLevel = Math.min(avg / 90, 1);
  requestAnimationFrame(medirVolume);
}

function pararAnaliseAudio() {
  if (micStream) micStream.getTracks().forEach(t => t.stop());
  if (audioCtx) audioCtx.close();
  window.jarvisState.audioLevel = 0;
}

// ---- reconhecimento de voz ----
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = 'pt-BR';
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onresult = async (e) => {
    const text = Array.from(e.results).map(r => r[0].transcript).join('');
    transcript.textContent = text.toUpperCase();

    if (!processando && text.trim().length > 2) {
      const comando = text.toLowerCase().trim();
      if (!comando) return;

      processando = true;
      try { recognition.stop(); } catch (e) {}

      setMode('thinking', 'PROCESSANDO');
      status.textContent = '◈ PROCESSANDO COMANDO ◈';
      transcript.textContent = comando.toUpperCase();
      adicionarMensagemChat('user', comando);

      const resposta = await enviarComando(comando);

      setMode('speaking', 'RESPONDENDO');
      speak(resposta);
      adicionarMensagemChat('jarvis', resposta);
      transcript.textContent = resposta.toUpperCase();

      setTimeout(() => {
        setMode(isListening ? 'listening' : 'idle', isListening ? 'OUVINDO' : 'J.A.R.V.I.S.');
        status.textContent = isListening ? '◈ MICROFONE ATIVO ◈' : '◈ AGUARDANDO COMANDO ◈';
        processando = false;
        if (isListening) {
          try { recognition.start(); } catch (e) {}
        }
      }, 2500);
    }
  };

  recognition.onerror = () => {
    status.textContent = '◈ ERRO DE MICROFONE · TENTE NOVAMENTE ◈';
  };

  recognition.onend = () => {
    if (isListening && !processando) {
      try { recognition.start(); } catch (e) {}
    }
  };
}

function speak(text) {
  // a síntese de fala real acontece no backend (ElevenLabs / fallback Windows)
  console.log("Jarvis:", text);
}

// ---- clique no núcleo ativa/desativa o microfone ----
coreCenter.addEventListener('click', () => {
  if (!SpeechRecognition) {
    status.textContent = '◈ BROWSER NÃO SUPORTA VOZ ◈';
    return;
  }

  if (isListening) {
    isListening = false;
    coreCenter.classList.remove('active');
    try { recognition.stop(); } catch (e) {}
    pararAnaliseAudio();
    setMode('idle', 'J.A.R.V.I.S.');
    status.textContent = '◈ MICROFONE DESLIGADO ◈';
    transcript.textContent = '';
  } else {
    isListening = true;
    coreCenter.classList.add('active');
    try { recognition.start(); } catch (e) {}
    iniciarAnaliseAudio();
    setMode('listening', 'OUVINDO');
    status.textContent = '◈ MICROFONE ATIVO ◈';
  }
});

// ---- teclado de texto ----
const textInput = document.getElementById('text-input');
const sendBtn    = document.getElementById('send-btn');
const stopBtn    = document.getElementById('stop-btn');

async function enviarTexto() {
  const comando = textInput.value.trim();
  if (!comando || processando) return;

  processando = true;
  try { if (recognition && isListening) recognition.stop(); } catch (e) {}

  setMode('thinking', 'PROCESSANDO');
  status.textContent = '◈ PROCESSANDO COMANDO ◈';
  transcript.textContent = comando.toUpperCase();
  adicionarMensagemChat('user', comando);
  textInput.value = '';

  const resposta = await enviarComando(comando);

  setMode('speaking', 'RESPONDENDO');
  speak(resposta);
  adicionarMensagemChat('jarvis', resposta);
  transcript.textContent = resposta.toUpperCase();
  status.textContent = '◈ AGUARDANDO COMANDO ◈';

  setTimeout(() => {
    setMode(isListening ? 'listening' : 'idle', isListening ? 'OUVINDO' : 'J.A.R.V.I.S.');
    processando = false;
    try { if (isListening && recognition) recognition.start(); } catch (e) {}
  }, 2500);
}

sendBtn.addEventListener('click', enviarTexto);

textInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') enviarTexto();
});

textInput.addEventListener('focus', () => {
  try { if (isListening && recognition) recognition.stop(); } catch (e) {}
});

textInput.addEventListener('blur', () => {
  setTimeout(() => {
    try { if (isListening && recognition) recognition.start(); } catch (e) {}
  }, 500);
});

// ---- botão parar fala ----
stopBtn.addEventListener('click', async () => {
  await fetch('/api/parar', { method: 'POST' });
  setMode(isListening ? 'listening' : 'idle');
  status.textContent = '◈ FALA INTERROMPIDA ◈';
  setTimeout(() => {
    status.textContent = isListening ? '◈ MICROFONE ATIVO ◈' : '◈ AGUARDANDO COMANDO ◈';
  }, 2000);
});
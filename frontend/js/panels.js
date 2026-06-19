// js/panels.js — Hora, localização, clima e chat lateral

// ---- RELÓGIO ----
function updateClock() {
  const now = new Date();
  const timeEl = document.getElementById('clockTime');
  const dateEl = document.getElementById('clockDate');
  if (timeEl) timeEl.textContent = now.toLocaleTimeString('pt-BR', { hour12: false });
  if (dateEl) {
    dateEl.textContent = now.toLocaleDateString('pt-BR', {
      weekday: 'long', day: '2-digit', month: 'long'
    }).toUpperCase();
  }
}
updateClock();
setInterval(updateClock, 1000);

// ---- CLIMA + LOCALIZAÇÃO ----
async function carregarClima() {
  try {
    const r = await fetch('/api/clima');
    const d = await r.json();

    if (d.erro) {
      document.getElementById('locationRow').textContent = '📍 INDISPONÍVEL';
      document.getElementById('weatherDesc').textContent = 'SEM DADOS';
      return;
    }

    document.getElementById('locationRow').textContent = `📍 ${d.cidade.toUpperCase()}, ${d.pais || ''}`;
    document.getElementById('weatherTemp').textContent = d.temp + '°';
    document.getElementById('weatherDesc').textContent = d.descricao;
    document.getElementById('weatherFeels').textContent = d.sensacao + '°';
    document.getElementById('weatherHumidity').textContent = d.umidade + '%';
    document.getElementById('weatherWind').textContent = d.vento + ' km/h';
  } catch (e) {
    console.log('Erro ao carregar clima:', e);
    document.getElementById('weatherDesc').textContent = 'ERRO DE CONEXÃO';
  }
}
carregarClima();
setInterval(carregarClima, 10 * 60 * 1000); // atualiza a cada 10 minutos

// ---- CHAT LATERAL ----
function adicionarMensagemChat(role, texto) {
  const chat = document.getElementById('chat-messages');
  if (!chat) return;

  // remove placeholder vazio se existir
  const empty = chat.querySelector('.chat-empty');
  if (empty) empty.remove();

  const msg = document.createElement('div');
  msg.className = `chat-msg ${role}`;
  msg.textContent = role === 'user' ? `▶ ${texto}` : `◈ ${texto}`;
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;

  while (chat.children.length > 60) {
    chat.removeChild(chat.firstChild);
  }
}

window.adicionarMensagemChat = adicionarMensagemChat;
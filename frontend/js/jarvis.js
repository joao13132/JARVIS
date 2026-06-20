// js/jarvis.js — Comunicação com o backend (autenticada)

const API_URL = '';

// ---- proteção de rota: exige login ----
const TOKEN = localStorage.getItem('jarvis_token');
if (!TOKEN) {
  window.location.href = '/login.html';
}

function getUsuario() {
  try {
    return JSON.parse(localStorage.getItem('jarvis_user') || '{}');
  } catch {
    return {};
  }
}

function logout() {
  localStorage.removeItem('jarvis_token');
  localStorage.removeItem('jarvis_user');
  window.location.href = '/login.html';
}

async function enviarComando(comando) {
  try {
    const resposta = await fetch(`${API_URL}/api/command`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${TOKEN}`
      },
      body: JSON.stringify({ command: comando })
    });

    if (resposta.status === 401) {
      logout();
      return 'Sessão expirada. Faça login novamente.';
    }

    const data = await resposta.json();
    return data.response;

  } catch (erro) {
    console.error('Erro ao conectar com Jarvis:', erro);
    return 'Desculpe, não consegui me conectar ao servidor.';
  }
}

async function apiAutenticada(rota, options = {}) {
  return fetch(`${API_URL}${rota}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
      'Authorization': `Bearer ${TOKEN}`
    }
  });
}
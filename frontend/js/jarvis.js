// js/jarvis.js — Comunicação com o backend

const API_URL = '';

async function enviarComando(comando) {
  try {
    const resposta = await fetch(`${API_URL}/api/command`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: comando })
    });

    const data = await resposta.json();
    return data.response;

  } catch (erro) {
    console.error('Erro ao conectar com Jarvis:', erro);
    return 'Desculpe, não consegui me conectar ao servidor.';
  }
}
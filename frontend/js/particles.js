// js/particles.js — Anel de partículas orgânico estilo Jarvis

(function () {
  const canvas = document.getElementById('particleCanvas');
  const ctx = canvas.getContext('2d');

  let W, H, CX, CY;
  let DPR = window.devicePixelRatio || 1;

  function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    W = rect.width;
    H = rect.height;
    canvas.width = W * DPR;
    canvas.height = H * DPR;
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    CX = W / 2;
    CY = H / 2;
  }
  window.addEventListener('resize', resize);
  resize();

  // ---- estado global controlado pelo main.js ----
  window.jarvisState = {
    mode: 'idle',        // idle | listening | thinking | speaking
    audioLevel: 0,        // 0 a 1, atualizado pelo analyser de voz
  };

  const COLORS = {
    idle:      { r: 29,  g: 233, b: 212 },
    listening: { r: 60,  g: 255, b: 230 },
    thinking:  { r: 255, g: 183, b: 77  },
    speaking:  { r: 29,  g: 233, b: 212 },
  };

  const BASE_RADIUS = 165;
  const RING_COUNT = 3;
  const PARTICLES_PER_RING = 90;

  // cria as partículas distribuídas em 3 "fitas" onduladas ao redor do núcleo
  const particles = [];
  for (let ring = 0; ring < RING_COUNT; ring++) {
    for (let i = 0; i < PARTICLES_PER_RING; i++) {
      const angle = (i / PARTICLES_PER_RING) * Math.PI * 2;
      particles.push({
        ring,
        baseAngle: angle,
        angleOffset: Math.random() * 0.4 - 0.2,
        speed: 0.0009 + ring * 0.00025 + Math.random() * 0.0003,
        direction: ring % 2 === 0 ? 1 : -1,
        waveSeed: Math.random() * Math.PI * 2,
        waveSpeed: 0.0014 + Math.random() * 0.001,
        waveAmp: 14 + Math.random() * 18,
        radiusJitter: Math.random() * 10,
        size: 0.7 + Math.random() * 1.6,
        opacity: 0.35 + Math.random() * 0.5,
        twinkleSeed: Math.random() * Math.PI * 2,
        twinkleSpeed: 0.002 + Math.random() * 0.004,
      });
    }
  }

  let t = 0;
  let rotationGlobal = 0;
  let pulsePhase = 0;

  function getModeColor() {
    return COLORS[window.jarvisState.mode] || COLORS.idle;
  }

  function getModeSpeedMultiplier() {
    switch (window.jarvisState.mode) {
      case 'thinking': return 2.6;
      case 'listening': return 1.4;
      case 'speaking': return 1.7;
      default: return 1;
    }
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);

    t += 1;
    const speedMult = getModeSpeedMultiplier();
    rotationGlobal += 0.0011 * speedMult;

    const color = getModeColor();
    const audioBoost = window.jarvisState.audioLevel * 28;

    // núcleo: leve pulsar contínuo + boost de áudio
    pulsePhase += 0.03;
    const breathing = Math.sin(pulsePhase) * 4;

    particles.forEach(p => {
      const ringRadiusBase = BASE_RADIUS + p.ring * 26 - 26;
      const wave = Math.sin(t * p.waveSpeed + p.waveSeed) * p.waveAmp * (0.5 + speedMult * 0.3);
      const radius = ringRadiusBase + wave + p.radiusJitter + breathing + audioBoost * (0.4 + p.ring * 0.2);

      const angle = p.baseAngle + p.angleOffset + rotationGlobal * p.direction * (1 + p.speed * 200 * speedMult);

      const x = CX + Math.cos(angle) * radius;
      const y = CY + Math.sin(angle) * radius * 0.94; // leve achatamento elíptico

      const twinkle = (Math.sin(t * p.twinkleSpeed + p.twinkleSeed) + 1) / 2;
      const alpha = p.opacity * (0.5 + twinkle * 0.5) * (window.jarvisState.mode === 'thinking' ? 1.15 : 1);

      ctx.beginPath();
      ctx.arc(x, y, p.size + audioBoost * 0.02, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${color.r},${color.g},${color.b},${Math.min(alpha, 1)})`;
      ctx.shadowColor = `rgba(${color.r},${color.g},${color.b},0.8)`;
      ctx.shadowBlur = 6;
      ctx.fill();
    });

    // linhas de conexão sutis entre partículas próximas do mesmo ring (efeito teia)
    if (window.jarvisState.mode !== 'idle') {
      ctx.strokeStyle = `rgba(${color.r},${color.g},${color.b},0.06)`;
      ctx.lineWidth = 0.5;
      for (let i = 0; i < particles.length; i += 7) {
        const p1 = particles[i];
        const p2 = particles[(i + 7) % particles.length];
        if (p1.ring !== p2.ring) continue;
        const a1 = p1.baseAngle + p1.angleOffset + rotationGlobal * p1.direction * (1 + p1.speed * 200 * speedMult);
        const a2 = p2.baseAngle + p2.angleOffset + rotationGlobal * p2.direction * (1 + p2.speed * 200 * speedMult);
        const r1 = BASE_RADIUS + p1.ring * 26 - 26 + Math.sin(t * p1.waveSpeed + p1.waveSeed) * p1.waveAmp + breathing;
        const r2 = BASE_RADIUS + p2.ring * 26 - 26 + Math.sin(t * p2.waveSpeed + p2.waveSeed) * p2.waveAmp + breathing;
        const x1 = CX + Math.cos(a1) * r1, y1 = CY + Math.sin(a1) * r1 * 0.94;
        const x2 = CX + Math.cos(a2) * r2, y2 = CY + Math.sin(a2) * r2 * 0.94;
        const dist = Math.hypot(x2 - x1, y2 - y1);
        if (dist < 40) {
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(draw);
  }

  draw();
})();
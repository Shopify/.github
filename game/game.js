(() => {
  const canvas = document.getElementById('board');
  const ctx = canvas.getContext('2d');
  const scoreEl = document.getElementById('score');
  const bestEl = document.getElementById('best');
  const startBtn = document.getElementById('startBtn');
  const pauseBtn = document.getElementById('pauseBtn');
  const restartBtn = document.getElementById('restartBtn');

  const GRID = 24; // 24x24 cells
  const CELL = canvas.width / GRID;
  const BASE_SPEED_MS = 120;

  const DIR = {
    UP: { x: 0, y: -1 },
    DOWN: { x: 0, y: 1 },
    LEFT: { x: -1, y: 0 },
    RIGHT: { x: 1, y: 0 },
  };

  let state = {
    snake: [{ x: 8, y: 12 }],
    dir: DIR.RIGHT,
    pendingDir: DIR.RIGHT,
    food: spawnFood([{ x: 8, y: 12 }]),
    score: 0,
    best: Number(localStorage.getItem('snake_best') || '0'),
    running: false,
    gameOver: false,
    tickMs: BASE_SPEED_MS,
    lastTickAt: 0,
  };

  bestEl.textContent = String(state.best);

  function spawnFood(occupied) {
    while (true) {
      const x = Math.floor(Math.random() * GRID);
      const y = Math.floor(Math.random() * GRID);
      if (!occupied.some(p => p.x === x && p.y === y)) return { x, y };
    }
  }

  function reset() {
    state.snake = [{ x: 8, y: 12 }];
    state.dir = DIR.RIGHT;
    state.pendingDir = DIR.RIGHT;
    state.food = spawnFood(state.snake);
    state.score = 0;
    state.running = false;
    state.gameOver = false;
    state.tickMs = BASE_SPEED_MS;
    scoreEl.textContent = '0';
    draw();
  }

  function start() {
    if (state.gameOver) reset();
    state.running = true;
  }

  function pause() { state.running = false; }

  function restart() { reset(); start(); }

  startBtn.addEventListener('click', start);
  pauseBtn.addEventListener('click', pause);
  restartBtn.addEventListener('click', restart);

  window.addEventListener('keydown', (e) => {
    const key = e.key.toLowerCase();
    if (key === 'p') { state.running = !state.running; return; }
    if (key === ' ' || key === 'enter') { if (!state.running) start(); return; }
    const map = {
      arrowup: DIR.UP,    w: DIR.UP,
      arrowdown: DIR.DOWN,  s: DIR.DOWN,
      arrowleft: DIR.LEFT,  a: DIR.LEFT,
      arrowright: DIR.RIGHT, d: DIR.RIGHT,
    };
    const next = map[key];
    if (!next) return;
    // Prevent reversing directly
    const isOpposite = (a, b) => a.x + b.x === 0 && a.y + b.y === 0;
    if (!isOpposite(next, state.dir)) state.pendingDir = next;
  });

  function tick(now) {
    if (!state.lastTickAt) state.lastTickAt = now;
    const elapsed = now - state.lastTickAt;
    if (state.running && elapsed >= state.tickMs) {
      state.lastTickAt = now;
      advance();
    }
    draw();
    requestAnimationFrame(tick);
  }

  function advance() {
    state.dir = state.pendingDir;
    const head = state.snake[0];
    const next = { x: head.x + state.dir.x, y: head.y + state.dir.y };

    // Wrap around edges
    next.x = (next.x + GRID) % GRID;
    next.y = (next.y + GRID) % GRID;

    // Self collision
    if (state.snake.some((p, i) => i !== 0 && p.x === next.x && p.y === next.y)) {
      state.running = false; state.gameOver = true; return;
    }

    // Move
    state.snake.unshift(next);

    // Eat
    if (next.x === state.food.x && next.y === state.food.y) {
      state.score += 1;
      scoreEl.textContent = String(state.score);
      state.food = spawnFood(state.snake);
      if (state.score % 5 === 0 && state.tickMs > 60) state.tickMs -= 5;
    } else {
      state.snake.pop();
    }

    // Best
    if (state.score > state.best) {
      state.best = state.score;
      localStorage.setItem('snake_best', String(state.best));
      bestEl.textContent = String(state.best);
    }
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Grid backdrop
    ctx.fillStyle = '#0b1a2b';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'rgba(255,255,255,0.04)';
    for (let i = 0; i <= GRID; i++) {
      ctx.beginPath();
      ctx.moveTo(i * CELL, 0); ctx.lineTo(i * CELL, canvas.height); ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * CELL); ctx.lineTo(canvas.width, i * CELL); ctx.stroke();
    }

    // Food
    drawCell(state.food.x, state.food.y, '#ff5d73');

    // Snake
    state.snake.forEach((p, idx) => {
      const tone = 180 + Math.min(60, idx * 2);
      drawCell(p.x, p.y, `hsl(${tone} 90% 60%)`);
    });

    if (!state.running) {
      ctx.fillStyle = 'rgba(5,11,18,0.6)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#cfe6ff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.font = 'bold 28px Inter, system-ui';
      ctx.fillText(state.gameOver ? 'Game Over' : 'Paused', canvas.width/2, canvas.height/2 - 14);
      ctx.font = '14px Inter, system-ui';
      ctx.fillText('Press Start or Space to play', canvas.width/2, canvas.height/2 + 14);
    }
  }

  function drawCell(x, y, color) {
    const px = x * CELL; const py = y * CELL;
    const r = 6;
    ctx.fillStyle = color;
    roundRect(ctx, px + 1, py + 1, CELL - 2, CELL - 2, r);
    ctx.fill();
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  reset();
  requestAnimationFrame(tick);
})();

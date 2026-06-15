const WORDS = [
  'скорость','точность','клавиша','гонка','победа','буква','текст','машина','финиш','игрок',
  'реакция','ритм','пальцы','экран','комната','турнир','профиль','книга','абзац','слово',
  'дорога','рывок','лидер','результат','ошибка','секунда','разгон','рекорд','соперник','трасса',
  'классика','спринт','навык','печать','режим','уровень','баллы','старт','таймер','поток'
];
const KEYS = 'йцукенгшщзхъфывапролджэячсмитьбю'.split('');

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function byId(id) {
  return document.getElementById(id);
}

async function submitMiniGameRecord(game, score) {
  try {
    const response = await fetch('/api/minigame-record/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({game, score})
    });
    return await response.json();
  } catch (error) {
    return {ok: false};
  }
}

function recordMessage(data) {
  if (!data || !data.ok) return '';
  if (data.new_record) return ` <span class="record-bonus">Новый рекорд! +10 💎</span>`;
  return ` <span class="record-bonus">+10 💎 за прохождение</span>`;
}

function initSprint() {
  const page = document.querySelector('[data-game="sprint"]');
  if (!page) return;

  const wordsBox = byId('sprintWords');
  const input = byId('sprintInput');
  const timeLeft = byId('timeLeft');
  const scoreBox = byId('score');
  const mistakesBox = byId('mistakes');
  const result = byId('sprintResult');
  const startBtn = byId('startSprint');
  const restartBtn = byId('restartSprint');
  let queue = [];
  let score = 0;
  let mistakes = 0;
  let time = 30;
  let active = false;
  let timer = null;

  function buildQueue() {
    queue = Array.from({length: 18}, () => pick(WORDS));
    renderQueue();
  }

  function renderQueue() {
    wordsBox.innerHTML = queue.map((word, index) => `<span class="${index === 0 ? 'active' : ''}">${word}</span>`).join('');
  }

  function reset() {
    clearInterval(timer);
    score = 0;
    mistakes = 0;
    time = 30;
    active = false;
    input.value = '';
    input.disabled = true;
    result.textContent = '';
    scoreBox.textContent = score;
    mistakesBox.textContent = mistakes;
    timeLeft.textContent = time;
    buildQueue();
  }

  async function finish() {
    active = false;
    input.disabled = true;
    clearInterval(timer);
    const record = await submitMiniGameRecord('sprint', score);
    result.innerHTML = `<strong>Итог:</strong> ${score} слов, ошибок: ${mistakes}.` + recordMessage(record);
  }

  startBtn.addEventListener('click', () => {
    reset();
    active = true;
    input.disabled = false;
    input.focus();
    timer = setInterval(() => {
      time -= 1;
      timeLeft.textContent = time;
      if (time <= 0) finish();
    }, 1000);
  });

  restartBtn.addEventListener('click', reset);

  input.addEventListener('keydown', (event) => {
    if (!active) return;
    if (event.key !== 'Enter' && event.key !== ' ') return;
    event.preventDefault();
    const typed = input.value.trim().toLowerCase();
    const target = queue[0];
    if (!typed) return;
    if (typed === target) {
      score += 1;
      queue.shift();
      queue.push(pick(WORDS));
      scoreBox.textContent = score;
    } else {
      mistakes += 1;
      mistakesBox.textContent = mistakes;
    }
    input.value = '';
    renderQueue();
  });

  reset();
}

function initFalling() {
  const page = document.querySelector('[data-game="falling"]');
  if (!page) return;

  const arena = byId('fallingArena');
  const input = byId('fallingInput');
  const scoreBox = byId('fallScore');
  const livesBox = byId('lives');
  const levelBox = byId('level');
  const result = byId('fallingResult');
  const startBtn = byId('startFalling');
  const restartBtn = byId('restartFalling');
  let words = [];
  let score = 0;
  let lives = 3;
  let level = 1;
  let active = false;
  let lastSpawn = 0;
  let raf = null;

  function reset() {
    active = false;
    cancelAnimationFrame(raf);
    arena.innerHTML = '';
    words = [];
    score = 0;
    lives = 3;
    level = 1;
    input.value = '';
    input.disabled = true;
    result.textContent = '';
    scoreBox.textContent = score;
    livesBox.textContent = lives;
    levelBox.textContent = level;
  }

  function spawn() {
    const el = document.createElement('div');
    el.className = 'falling-word';
    el.textContent = pick(WORDS);
    el.style.left = `${Math.random() * 78 + 4}%`;
    arena.appendChild(el);
    words.push({el, y: -10, word: el.textContent});
  }

  async function finish() {
    active = false;
    input.disabled = true;
    cancelAnimationFrame(raf);
    const record = await submitMiniGameRecord('falling', score);
    result.innerHTML = `<strong>Игра окончена:</strong> ${score} слов.` + recordMessage(record);
  }

  function loop(ts) {
    if (!active) return;
    if (!lastSpawn || ts - lastSpawn > Math.max(620, 1500 - score * 25)) {
      spawn();
      lastSpawn = ts;
    }
    const speed = 0.12 + score * 0.004;
    level = Math.max(1, Math.floor(score / 6) + 1);
    levelBox.textContent = level;
    words.forEach((item) => {
      item.y += speed;
      item.el.style.top = `${item.y}%`;
    });
    words = words.filter((item) => {
      if (item.y < 94) return true;
      item.el.remove();
      lives -= 1;
      livesBox.textContent = lives;
      if (lives <= 0) finish();
      return false;
    });
    raf = requestAnimationFrame(loop);
  }

  startBtn.addEventListener('click', () => {
    reset();
    active = true;
    input.disabled = false;
    input.focus();
    lastSpawn = 0;
    raf = requestAnimationFrame(loop);
  });

  restartBtn.addEventListener('click', reset);

  input.addEventListener('input', () => {
    if (!active) return;
    const value = input.value.trim().toLowerCase();
    const index = words.findIndex((item) => item.word === value);
    if (index === -1) return;
    words[index].el.remove();
    words.splice(index, 1);
    score += 1;
    scoreBox.textContent = score;
    input.value = '';
  });

  reset();
}

function initReaction() {
  const page = document.querySelector('[data-game="reaction"]');
  if (!page) return;

  const keyBox = byId('reactionKey');
  const roundBox = byId('round');
  const avgBox = byId('avgReaction');
  const mistakesBox = byId('reactionMistakes');
  const result = byId('reactionResult');
  const startBtn = byId('startReaction');
  const restartBtn = byId('restartReaction');
  let current = '';
  let startedAt = 0;
  let round = 0;
  let mistakes = 0;
  let times = [];
  let active = false;

  function avg() {
    if (!times.length) return 0;
    return Math.round(times.reduce((a, b) => a + b, 0) / times.length);
  }

  function nextKey() {
    if (round >= 20) {
      active = false;
      keyBox.textContent = '✓';
      const average = avg();
      submitMiniGameRecord('reaction', average).then(record => {
        result.innerHTML = `<strong>Итог:</strong> средняя реакция ${average} мс, ошибок: ${mistakes}.` + recordMessage(record);
      });
      return;
    }
    current = pick(KEYS);
    round += 1;
    roundBox.textContent = round;
    keyBox.textContent = current.toUpperCase();
    startedAt = performance.now();
  }

  function reset() {
    current = '';
    round = 0;
    mistakes = 0;
    times = [];
    active = false;
    keyBox.textContent = '?';
    roundBox.textContent = 0;
    avgBox.textContent = 0;
    mistakesBox.textContent = 0;
    result.textContent = '';
  }

  startBtn.addEventListener('click', () => {
    reset();
    active = true;
    nextKey();
  });

  restartBtn.addEventListener('click', reset);

  document.addEventListener('keydown', (event) => {
    if (!active || !current) return;
    const key = event.key.toLowerCase();
    if (key === current) {
      times.push(Math.round(performance.now() - startedAt));
      avgBox.textContent = avg();
      nextKey();
    } else if (key.length === 1) {
      mistakes += 1;
      mistakesBox.textContent = mistakes;
      keyBox.classList.remove('wrong-hit');
      void keyBox.offsetWidth;
      keyBox.classList.add('wrong-hit');
    }
  });

  reset();
}

initSprint();
initFalling();
initReaction();

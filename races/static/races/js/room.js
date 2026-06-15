const page = document.querySelector('.room-page');
const code = page.dataset.code;
const playerName = page.dataset.player;
const serverSelectedSkin = page.dataset.skin || 'car_01';
const textBox = document.getElementById('text');
const input = document.getElementById('input');
const startBtn = document.getElementById('startBtn');
const playersBox = document.getElementById('players');
const trackBox = document.getElementById('track');
const roleBadge = document.getElementById('roleBadge');
const finishInfo = document.getElementById('finishInfo');
const countdownBox = document.getElementById('countdownBox');

let target = '';
let startedAt = null;
let finishedSent = false;
let youAreSpectator = false;
let isOwner = false;
let totalErrors = 0;
let lastTyped = '';
let lastSentProgress = 0;
const protocol = location.protocol === 'https:' ? 'wss' : 'ws';

function sameTypingChar(a, b) {
  if (window.TypeWorldCore && TypeWorldCore.charsEqualForTyping) return TypeWorldCore.charsEqualForTyping(a, b);
  return String(a || '').replace('ё', 'е').replace('Ё', 'Е') === String(b || '').replace('ё', 'е').replace('Ё', 'Е');
}
function sameTypingText(a, b) {
  if (window.TypeWorldCore && TypeWorldCore.textsEqualForTyping) return TypeWorldCore.textsEqualForTyping(a, b);
  return String(a || '').replaceAll('ё', 'е').replaceAll('Ё', 'Е') === String(b || '').replaceAll('ё', 'е').replaceAll('Ё', 'Е');
}
const allSkins = ['car_01','car_02','car_03','car_04','car_05','car_06','car_07','car_08','car_09','car_10','car_11','cyber_01','cyber_02','cyber_03','cyber_04','cyber_05','cyber_06','cyber_07','cyber_08','cyber_09','cyber_10'];
const unlockedSkinsNode = document.getElementById('unlockedSkinsData');
const availableSkins = unlockedSkinsNode ? JSON.parse(unlockedSkinsNode.textContent || '["car_01"]') : ['car_01'];
const oldSkinMap = {red:'car_01', blue:'car_02', green:'car_04', yellow:'car_03', purple:'car_07'};
function normalizeSkin(value){
  const mapped = oldSkinMap[value] || value || 'car_01';
  return availableSkins.includes(mapped) ? mapped : 'car_01';
}
let selectedSkin = normalizeSkin(serverSelectedSkin || localStorage.getItem('typeworld_car_skin'));
localStorage.setItem('typeworld_car_skin', selectedSkin);
const socket = new WebSocket(`${protocol}://${location.host}/ws/room/${code}/?name=${encodeURIComponent(playerName)}&skin=${encodeURIComponent(selectedSkin)}`);

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'countdown') {
    showCountdown(data.remaining);
    input.disabled = true;
    startBtn.disabled = true;
    return;
  }
  if (data.type === 'start') {
    if (!youAreSpectator && !finishedSent) {
      totalErrors = 0;
      lastTyped = '';
      lastSentProgress = 0;
      input.disabled = false;
      hideCountdown();
      input.value = '';
      TypeWorldCore.renderText(textBox, target, '');
      input.focus();
      startedAt = Date.now();
    }
    return;
  }
  if (data.type === 'finish') {
    input.disabled = true;
    finishInfo.textContent = 'Гонка завершена. Комната будет удалена, результаты уже сохранены.';
    return;
  }
  if (data.type === 'deleted') {
    finishInfo.textContent = data.message;
    startBtn.disabled = true;
    input.disabled = true;
    return;
  }
  if (data.type === 'state') {
    target = data.text || target;
    youAreSpectator = Boolean(data.youAreSpectator);
    isOwner = Boolean(data.isOwner);
    document.getElementById('book').textContent = data.book || 'Русская книга';
    document.getElementById('author').textContent = data.author || '';
    document.getElementById('source').textContent = data.source || 'Источник';
    document.getElementById('winner').textContent = data.winner ? `Победитель: ${data.winner}` : '';
    roleBadge.textContent = youAreSpectator ? 'Роль: зритель' : (isOwner ? 'Роль: создатель комнаты' : 'Роль: игрок');
    if (!input.value) TypeWorldCore.renderText(textBox, target, '');
    renderPlayers(data.players || []);
    renderTrack(data.players || []);
    renderResults(data.results || [], data.players || []);
    startBtn.disabled = data.started || data.countdown || data.finished || youAreSpectator || !isOwner;
    startBtn.textContent = isOwner ? 'Старт гонки' : 'Ждём создателя';
    if (data.countdown) {
      showCountdown(data.countdownRemaining || 10);
    } else if (!data.started) {
      hideCountdown();
    }
    if (youAreSpectator) {
      input.disabled = true;
      input.placeholder = 'Гонка уже началась. Вы подключены как зритель.';
    } else if (data.countdown) {
      input.disabled = true;
      input.placeholder = 'Гонка начнётся после таймера...';
    } else if (data.started && !data.finished && !finishedSent && !startedAt) {
      input.disabled = false;
      startedAt = Date.now();
    }
    if (data.finished) {
      input.disabled = true;
      finishInfo.textContent = 'Гонка завершена. Комната будет удалена через несколько секунд.';
    }
  }
};

socket.onclose = () => {
  input.disabled = true;
  startBtn.disabled = true;
};

startBtn.onclick = () => {
  if (!isOwner || youAreSpectator || startBtn.disabled) return;
  socket.send(JSON.stringify({action:'start'}));
};
input.addEventListener('input', () => {
  if (youAreSpectator || finishedSent) {
    input.disabled = true;
    return;
  }

  if (input.value.length > target.length) {
    input.value = input.value.slice(0, target.length);
  }

  if (!startedAt) startedAt = Date.now();

  const typed = input.value;
  registerNewMistakes(typed);
  lastTyped = typed;

  TypeWorldCore.renderText(textBox, target, typed);
  const s = calcRaceStats(target, typed, startedAt, totalErrors);

  document.getElementById('wpm').textContent = s.wpm;
  document.getElementById('accuracy').textContent = s.accuracy.toFixed(1);
  document.getElementById('errors').textContent = s.errors;

  lastSentProgress = s.progress;

  if (s.finished) {
    input.disabled = true;
    finishedSent = true;
    finishInfo.textContent = 'Вы финишировали. Ждём остальных игроков...';
  }

  socket.send(JSON.stringify({
    action:'progress',
    progress:s.progress,
    wpm:s.wpm,
    accuracy:s.accuracy,
    errors:s.errors,
    finished:s.finished
  }));
});

function showCountdown(remaining) {
  if (!countdownBox) return;
  countdownBox.hidden = false;
  countdownBox.textContent = remaining > 0 ? `Старт через ${remaining}` : 'Старт!';
}

function hideCountdown() {
  if (!countdownBox) return;
  countdownBox.hidden = true;
  countdownBox.textContent = '';
}

function renderTrack(players) {
  const list = players.length ? players : [];
  updateRaceLayoutForPlayers(list);
  if (!list.length) {
    trackBox.innerHTML = '<div class="track-empty">Пока на трассе никого нет</div>';
    return;
  }

  const empty = trackBox.querySelector('.track-empty');
  if (empty) empty.remove();

  let finish = trackBox.querySelector('.finish-line');
  if (!finish) {
    finish = document.createElement('div');
    finish.className = 'finish-line';
    trackBox.appendChild(finish);
  }

  const aliveKeys = new Set();
  list.forEach((p, index) => {
    const key = slugify(p.name || ('player-' + index));
    aliveKeys.add(key);
    const progress = Math.max(0, Math.min(100, Number(p.progress) || 0));
    let lane = trackBox.querySelector(`.track-lane[data-player-key="${key}"]`);
    const skin = allSkins.includes(p.skin) ? p.skin : allSkins[index % allSkins.length];

    if (!lane) {
      lane = document.createElement('div');
      lane.className = 'track-lane';
      lane.dataset.playerKey = key;
      lane.dataset.progress = String(progress);
      lane.innerHTML = `
        <div class="lane-name"></div>
        <div class="lane-progress"></div>
        <div class="lane-trail"></div>
        <img class="race-car" alt="Машинка игрока ${escapeHtml(p.name)}">
      `;
      trackBox.appendChild(lane);
    }

    lane.classList.toggle('spectator-lane', Boolean(p.spectator));
    lane.dataset.progress = String(progress);
    lane.querySelector('.lane-name').textContent = `${p.name}${p.spectator ? ' · зритель' : ''}`;
    lane.querySelector('.lane-progress').textContent = `${progress}%`;

    const trail = lane.querySelector('.lane-trail');
    const car = lane.querySelector('.race-car');
    if (p.spectator) {
      if (trail) trail.style.display = 'none';
      if (car) car.style.display = 'none';
      if (!lane.querySelector('.spectator-icon')) {
        const eye = document.createElement('div');
        eye.className = 'spectator-icon';
        eye.textContent = '👁️';
        lane.appendChild(eye);
      }
    } else {
      const eye = lane.querySelector('.spectator-icon');
      if (eye) eye.remove();
      if (trail) trail.style.display = '';
      if (car) {
        car.style.display = '';
        car.className = p.finished ? 'race-car finished' : 'race-car';
        const nextSrc = `/static/races/cars/${skin}.png?v=cyber-clean-2`;
        if (!car.src.endsWith(nextSrc)) car.src = nextSrc;
      }
    }
  });

  trackBox.querySelectorAll('.track-lane').forEach((lane) => {
    if (!aliveKeys.has(lane.dataset.playerKey)) lane.remove();
  });
  positionCarsInsideLanes();
}

function updateRaceLayoutForPlayers(players) {
  const count = Math.max(0, players.filter(p => !p.spectator).length || players.length || 0);
  const screen = document.querySelector('.race-screen');
  const card = document.querySelector('.wide-race-card');
  const classes = ['players-0','players-1','players-2','players-3','players-4','players-5','players-6','players-many'];
  [trackBox, screen, card].forEach(el => {
    if (!el) return;
    el.classList.remove(...classes);
    el.classList.add(count >= 7 ? 'players-many' : `players-${count}`);
  });
}

function registerNewMistakes(typed) {
  if (typed.length > lastTyped.length && typed.startsWith(lastTyped)) {
    for (let i = lastTyped.length; i < typed.length; i++) {
      if (!sameTypingChar(typed[i], target[i])) totalErrors += 1;
    }
    return;
  }

  let newlyWrong = 0;
  const max = Math.min(typed.length, target.length);
  for (let i = 0; i < max; i++) {
    if (!sameTypingChar(typed[i], target[i]) && (lastTyped[i] === undefined || sameTypingChar(lastTyped[i], target[i]))) {
      newlyWrong += 1;
    }
  }
  totalErrors += newlyWrong;
}

function correctPrefixLength(targetText, typedText) {
  let count = 0;
  const max = Math.min(targetText.length, typedText.length);
  while (count < max && sameTypingChar(typedText[count], targetText[count])) count += 1;
  return count;
}

function calcRaceStats(targetText, typedText, startTime, lifetimeErrors) {
  const correctPrefix = correctPrefixLength(targetText, typedText);
  const minutes = Math.max((Date.now() - startTime) / 60000, 0.01);
  const wpm = Math.round((correctPrefix / 5) / minutes);
  const attempts = correctPrefix + lifetimeErrors;
  const accuracy = attempts ? Math.max(0, (correctPrefix / attempts) * 100) : 100;
  const progress = targetText.length ? Math.min(100, Math.round((correctPrefix / targetText.length) * 100)) : 0;
  const finished = typedText.length >= targetText.length && sameTypingText(typedText.slice(0, targetText.length), targetText) && targetText.length > 0;
  return {errors:lifetimeErrors, wpm, accuracy, progress, finished};
}

function slugify(value) {
  return String(value).replace(/[^a-zA-Z0-9А-Яа-я_-]/g, '_');
}

function positionCarsInsideLanes() {
  const lanes = trackBox.querySelectorAll('.track-lane');
  lanes.forEach((lane) => {
    const car = lane.querySelector('.race-car');
    const trail = lane.querySelector('.lane-trail');
    if (!car) return;

    const progress = Math.max(0, Math.min(100, Number(lane.dataset.progress) || 0));
    const laneWidth = lane.clientWidth;
    const carWidth = car.offsetWidth || 72;
    const leftPadding = 14;
    const rightPadding = 14;

    const maxLeft = Math.max(leftPadding, laneWidth - carWidth - rightPadding);
    const left = leftPadding + (progress / 100) * (maxLeft - leftPadding);

    car.style.left = `${left}px`;
    if (trail) {
      const trailWidth = Math.min(laneWidth - leftPadding - rightPadding, left + carWidth * 0.78 - leftPadding);
      trail.style.width = `${Math.max(0, trailWidth)}px`;
    }
  });
}

window.addEventListener('resize', positionCarsInsideLanes);

function renderPlayers(players) {
  if (!playersBox) return;
  playersBox.hidden = true;
  playersBox.innerHTML = '';
  return;
  players.forEach(p => {
    const el = document.createElement('div');
    el.className = 'player';
    const role = p.spectator ? 'зритель' : (p.finished ? 'финиш' : 'игрок');
    el.innerHTML = `<div class="player-top"><strong>${escapeHtml(p.name)}</strong><span>${role} · ${p.progress}% · ${p.wpm} WPM</span></div><div class="bar"><span style="width:${p.progress}%"></span></div>`;
    playersBox.appendChild(el);
  });
}
function ensureTrackResultsPanel() {
  let panel = document.getElementById('trackResultsPanel');
  if (panel) return panel;

  panel = document.createElement('div');
  panel.id = 'trackResultsPanel';
  panel.className = 'input-results-card';
  panel.hidden = true;
  panel.innerHTML = `
    <div class="winner-results-title">🏆 Итоги гонки</div>
    <div id="trackWinnerName" class="winner-results-name"></div>
    <table class="winner-results-table">
      <thead><tr><th>#</th><th>Игрок</th><th>WPM</th><th>%</th></tr></thead>
      <tbody id="trackResultsBody"></tbody>
    </table>
  `;

  const input = document.getElementById('input');
  const typingCard = document.querySelector('.typing-card');
  if (input && input.parentNode) {
    input.insertAdjacentElement('afterend', panel);
  } else if (typingCard) {
    typingCard.appendChild(panel);
  } else {
    document.body.appendChild(panel);
  }
  return panel;
}

function renderResults(results, players) {
  const finishedPlayers = players
    .filter(p => p.finished && !p.spectator)
    .map(p => ({player_name:p.name, wpm:p.wpm, accuracy:p.accuracy, errors:p.errors, user_id:p.user_id, profile_url:p.profile_url}));
  const rows = (results.length ? results : finishedPlayers)
    .sort((a,b) => (b.wpm - a.wpm) || (b.accuracy - a.accuracy) || (a.errors - b.errors));

  const panel = ensureTrackResultsPanel();
  const body = document.getElementById('trackResultsBody');
  const winnerName = document.getElementById('trackWinnerName');

  panel.hidden = rows.length === 0;
  document.body.classList.toggle('race-results-open', rows.length > 0);
  body.innerHTML = '';

  trackBox.querySelectorAll('.track-lane').forEach(lane => lane.classList.remove('winner-lane'));

  if (!rows.length) return;

  const winner = rows[0];
  winnerName.textContent = `Победитель: ${winner.player_name}`;

  rows.slice(0, 6).forEach((r, index) => {
    const tr = document.createElement('tr');
    const profileUrl = r.profile_url || (r.user_id ? `/profile/${r.user_id}/` : '');
    const playerCell = profileUrl ? `<a class="profile-link" href="${profileUrl}">${escapeHtml(r.player_name)}</a>` : escapeHtml(r.player_name);
    tr.innerHTML = `<td>${index + 1}</td><td>${playerCell}</td><td>${r.wpm}</td><td>${Number(r.accuracy).toFixed(0)}%</td>`;
    body.appendChild(tr);
  });

  const winnerLane = trackBox.querySelector(`.track-lane[data-player-key="${slugify(winner.player_name)}"]`);
  if (winnerLane) {
    winnerLane.classList.add('winner-lane');
  }
}
function escapeHtml(str){return String(str).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}

(function enableTypeWorldCopyGuard(){
  const textBox = document.getElementById('text');
  const typingInput = document.getElementById('input');

  function showGuardMessage(message) {
    if (!typingInput) return;
    let warning = document.getElementById('copyGuardWarning');
    if (!warning) {
      warning = document.createElement('div');
      warning.id = 'copyGuardWarning';
      warning.className = 'copy-guard-warning';
      typingInput.insertAdjacentElement('afterend', warning);
    }
    warning.textContent = message;
    clearTimeout(window.__typeworldCopyGuardTimer);
    window.__typeworldCopyGuardTimer = setTimeout(() => {
      warning.textContent = '';
    }, 1800);
  }

  function insideRaceText(target) {
    return Boolean(target && target.closest && target.closest('.typing-text'));
  }

  document.addEventListener('copy', (event) => {
    if (insideRaceText(event.target)) {
      event.preventDefault();
      showGuardMessage('Копирование текста гонки запрещено.');
    }
  });

  document.addEventListener('cut', (event) => {
    if (insideRaceText(event.target)) {
      event.preventDefault();
    }
  });

  document.addEventListener('selectstart', (event) => {
    if (insideRaceText(event.target)) {
      event.preventDefault();
    }
  });

  document.addEventListener('dragstart', (event) => {
    if (insideRaceText(event.target)) {
      event.preventDefault();
    }
  });

  document.addEventListener('contextmenu', (event) => {
    if (insideRaceText(event.target) || event.target === typingInput) {
      event.preventDefault();
    }
  });

  document.addEventListener('keydown', (event) => {
    const key = (event.key || '').toLowerCase();
    const combo = event.ctrlKey || event.metaKey;
    if (combo && ['c', 'x', 'a'].includes(key) && insideRaceText(event.target)) {
      event.preventDefault();
      showGuardMessage('Выделение и копирование текста запрещены.');
    }
    if (typingInput && event.target === typingInput && combo && key === 'v') {
      event.preventDefault();
      showGuardMessage('Вставка в поле ввода запрещена. Печатай вручную.');
    }
  });

  if (typingInput) {
    ['paste', 'drop'].forEach((eventName) => {
      typingInput.addEventListener(eventName, (event) => {
        event.preventDefault();
        showGuardMessage('Вставка в поле ввода запрещена. Печатай вручную.');
      });
    });
  }

  if (textBox) {
    textBox.setAttribute('draggable', 'false');
    textBox.setAttribute('oncopy', 'return false');
    textBox.setAttribute('oncut', 'return false');
    textBox.setAttribute('onpaste', 'return false');
  }
})();

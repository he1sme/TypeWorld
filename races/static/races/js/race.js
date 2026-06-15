const textBox = document.querySelector('#text');
const input = document.querySelector('#input');
const wpmEl = document.querySelector('#wpm');
const accuracyEl = document.querySelector('#accuracy');
const timerEl = document.querySelector('#timer');
const statusEl = document.querySelector('#status');
const restartBtn = document.querySelector('#restart');
const raceCard = document.querySelector('.race-card');

const originalText = textBox.textContent.trim();
let startedAt = null;
let timer = null;
let finished = false;

function sameTypingChar(a, b) {
    return String(a || '').replace('ё', 'е').replace('Ё', 'Е') === String(b || '').replace('ё', 'е').replace('Ё', 'Е');
}

function sameTypingText(a, b) {
    return String(a || '').replaceAll('ё', 'е').replaceAll('Ё', 'Е') === String(b || '').replaceAll('ё', 'е').replaceAll('Ё', 'Е');
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function renderText(value = '') {
    textBox.innerHTML = '';
    [...originalText].forEach((char, index) => {
        const span = document.createElement('span');
        span.textContent = char;
        if (index < value.length) {
            span.className = sameTypingChar(value[index], char) ? 'correct' : 'wrong';
        } else if (index === value.length) {
            span.className = 'current';
        }
        textBox.appendChild(span);
    });
}

function calculate(value) {
    const elapsed = startedAt ? (Date.now() - startedAt) / 1000 : 0;
    const typed = value.length;
    let mistakes = 0;
    [...value].forEach((char, index) => {
        if (!sameTypingChar(char, originalText[index])) mistakes++;
    });
    const correct = Math.max(0, typed - mistakes);
    const accuracy = typed ? Math.max(0, (correct / typed) * 100) : 100;
    const words = correct / 5;
    const wpm = elapsed > 0 ? Math.round(words / (elapsed / 60)) : 0;
    return { elapsed, mistakes, accuracy, wpm };
}

function updateMetrics() {
    const metrics = calculate(input.value);
    wpmEl.textContent = metrics.wpm;
    accuracyEl.textContent = metrics.accuracy.toFixed(0);
    timerEl.textContent = metrics.elapsed.toFixed(1);
}

async function saveResult(metrics) {
    const response = await fetch('/api/result/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            text_id: raceCard.dataset.textId,
            wpm: metrics.wpm,
            accuracy: metrics.accuracy,
            mistakes: metrics.mistakes,
            duration_seconds: metrics.elapsed,
            player_name: 'Гость',
        }),
    });
    return response.ok;
}

input.addEventListener('input', async () => {
    if (finished) return;
    if (!startedAt) {
        startedAt = Date.now();
        timer = setInterval(updateMetrics, 100);
    }
    const value = input.value;
    renderText(value);
    updateMetrics();

    if (value.length >= originalText.length && sameTypingText(value.slice(0, originalText.length), originalText)) {
        finished = true;
        clearInterval(timer);
        input.disabled = true;
        const metrics = calculate(value.slice(0, originalText.length));
        updateMetrics();
        const ok = await saveResult(metrics);
        statusEl.textContent = ok ? `Финиш! Результат сохранён: ${metrics.wpm} WPM.` : 'Финиш, но результат не удалось сохранить.';
    }
});

restartBtn.addEventListener('click', () => window.location.reload());
renderText();

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

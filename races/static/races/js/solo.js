const page = document.querySelector('.race-page');
const target = page.dataset.text;
const textBox = document.getElementById('text');
const input = document.getElementById('input');
let startedAt = null;
let saved = false;
TypeWorldCore.renderText(textBox, target, '');
input.addEventListener('input', async () => {
  if (saved) {
    input.disabled = true;
    return;
  }
  if (input.value.length > target.length) input.value = input.value.slice(0, target.length);
  if (!startedAt) startedAt = Date.now();
  const typed = input.value;
  TypeWorldCore.renderText(textBox, target, typed);
  const s = TypeWorldCore.calcStats(target, typed, startedAt);
  document.getElementById('wpm').textContent = s.wpm;
  document.getElementById('accuracy').textContent = s.accuracy.toFixed(1);
  document.getElementById('errors').textContent = s.errors;
  if (s.finished && !saved) {
    saved = true;
    input.disabled = true;
    await fetch('/api/result/', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({wpm:s.wpm, accuracy:s.accuracy, errors:s.errors, player_name:'Solo'})});
  }
});

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

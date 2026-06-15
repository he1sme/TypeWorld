function normalizeCharForCompare(ch) {
  return String(ch || '').replace('ё', 'е').replace('Ё', 'Е');
}

function normalizeTextForCompare(text) {
  return String(text || '').replaceAll('ё', 'е').replaceAll('Ё', 'Е');
}

function charsEqualForTyping(typedChar, targetChar) {
  return normalizeCharForCompare(typedChar) === normalizeCharForCompare(targetChar);
}

function textsEqualForTyping(typedText, targetText) {
  return normalizeTextForCompare(typedText) === normalizeTextForCompare(targetText);
}

function renderText(container, target, typed) {
  container.innerHTML = '';
  for (let i = 0; i < target.length; i++) {
    const span = document.createElement('span');
    span.textContent = target[i];
    if (i < typed.length) span.className = charsEqualForTyping(typed[i], target[i]) ? 'correct' : 'wrong';
    else if (i === typed.length) span.className = 'current';
    container.appendChild(span);
  }
}
function calcStats(target, typed, startTime) {
  typed = typed.slice(0, target.length);
  let errors = 0;
  for (let i = 0; i < typed.length; i++) if (!charsEqualForTyping(typed[i], target[i])) errors++;
  const minutes = Math.max((Date.now() - startTime) / 60000, 0.01);
  const correctChars = Math.max(typed.length - errors, 0);
  const wpm = Math.round((correctChars / 5) / minutes);
  const accuracy = typed.length ? Math.max(0, ((typed.length - errors) / typed.length) * 100) : 100;
  const progress = target.length ? Math.min(100, Math.round((typed.length / target.length) * 100)) : 0;
  return {errors, wpm, accuracy, progress, finished: typed.length >= target.length && textsEqualForTyping(typed, target)};
}
window.TypeWorldCore = {renderText, calcStats, normalizeCharForCompare, normalizeTextForCompare, charsEqualForTyping, textsEqualForTyping};

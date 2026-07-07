import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');

test('submit button turns into the next question action after submission', () => {
  assert.doesNotMatch(html, /id="next-question"/);
  assert.match(html, /elements\.submitAnswer\.textContent = '提交';/);
  assert.match(html, /elements\.submitAnswer\.textContent = state\.answered \? '下一题' : '提交';/);
  assert.match(html, /state\.answered = true;[\s\S]*?renderQuestionMeta\(\);/);
  assert.match(html, /if \(state\.answered\) \{\s+chooseNextQuestion\(\);\s+return;\s+\}/);
});

test('wrong book is a separate app view instead of a sidebar list', () => {
  assert.match(html, /id="practice-view"/);
  assert.match(html, /id="wrong-book-view"/);
  assert.match(html, /data-view="practice"[^>]*>刷题<\/button>/);
  assert.match(html, /data-view="wrongBook"[^>]*>错题本<\/button>/);
  assert.doesNotMatch(html, /<aside class="side" aria-label="错题和数据">[\s\S]*<h2>错题本<\/h2>/);
  assert.match(html, /id="wrong-subject-filter"/);
  assert.match(html, /id="wrong-type-filter"/);
  assert.match(html, /id="wrong-book-list"/);
  assert.match(html, /function switchView\(view\)/);
});

test('favorites are shown in a separate app view', () => {
  assert.match(html, /id="favorite-view"/);
  assert.match(html, /data-view="favorite"[^>]*>收藏<\/button>/);
  assert.match(html, /id="favorite-subject-filter"/);
  assert.match(html, /id="favorite-type-filter"/);
  assert.match(html, /id="favorite-list"/);
  assert.match(html, /function renderFavoriteBook\(\)/);
  assert.match(html, /if \(isFavorite\) renderFavoriteBook\(\);/);
});

test('question bank is loaded from sibling files instead of embedded in index', () => {
  assert.doesNotMatch(html, /id="question-data"/);
  assert.doesNotMatch(html, /<script type="application\/json"/);
  assert.match(html, /<script src="question_bank_combined_en_schema\.js"><\/script>/);
  assert.match(html, /window\.QUESTION_BANK/);
  assert.equal(existsSync(new URL('../question_bank_combined_en_schema.json', import.meta.url)), true);
  assert.equal(existsSync(new URL('../question_bank_combined_en_schema.js', import.meta.url)), true);
});

test('question metadata does not reveal the correct answer before submission', () => {
  assert.doesNotMatch(html, /<span class="pill">答案 \$\{correctText\}<\/span>/);
  assert.doesNotMatch(html, /<span class="pill">答案 \$\{\{correctText\}\}<\/span>/);
});

test('favorite and mastered toggles do not reset submitted question state', () => {
  const favoriteBody = html.match(/function toggleFavorite\(\) \{([\s\S]*?)\n\}/)?.[1] || '';
  const masteredBody = html.match(/function toggleMastered\(\) \{([\s\S]*?)\n\}/)?.[1] || '';

  assert.match(html, /elements\.submitAnswer\.textContent = state\.answered \? '下一题' : '提交';/);
  assert.doesNotMatch(favoriteBody, /renderQuestion\(\)/);
  assert.doesNotMatch(masteredBody, /renderQuestion\(\)/);
  assert.match(favoriteBody, /renderQuestionMeta\(\)/);
  assert.match(masteredBody, /renderQuestionMeta\(\)/);
});

test('practice toolbar can shuffle option values while keeping visible labels fixed', () => {
  assert.match(html, /id="shuffle-options"/);
  assert.match(html, /shuffleOptions: document\.getElementById\('shuffle-options'\),/);
  assert.match(html, /function getDisplayOptionEntries\(question\)/);
  assert.match(html, /Core\.shuffleOptionValues\(entries\)/);
  assert.match(html, /Core\.getDisplayedCorrectAnswer\(displayEntries, question\.correct_answer\)/);
  assert.match(html, /return \{[\s\S]*shuffleOptionValues,[\s\S]*getDisplayedCorrectAnswer,/);
  assert.match(html, /button\.dataset\.key = key;/);
  assert.match(html, /button\.dataset\.originalKey = originalKey;/);
});

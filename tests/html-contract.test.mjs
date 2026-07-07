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
  assert.match(html, /<script src="x_same_series_selected_renamed\.js"><\/script>/);
  assert.match(html, /window\.QUESTION_BANK/);
  assert.match(html, /window\.SAME_SERIES_BANK/);
  assert.equal(existsSync(new URL('../question_bank_combined_en_schema.json', import.meta.url)), true);
  assert.equal(existsSync(new URL('../question_bank_combined_en_schema.js', import.meta.url)), true);
  assert.equal(existsSync(new URL('../x_same_series_selected_renamed.json', import.meta.url)), true);
  assert.equal(existsSync(new URL('../x_same_series_selected_renamed.js', import.meta.url)), true);
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

test('practice toolbar can switch between weighted and uniform question picking', () => {
  assert.match(html, /id="weight-mode-filter"/);
  assert.match(html, /<option value="weighted">错题加权<\/option>/);
  assert.match(html, /<option value="uniform">不加权<\/option>/);
  assert.match(html, /weightModeFilter: document\.getElementById\('weight-mode-filter'\),/);
  assert.match(html, /elements\.weightModeFilter\.value === 'uniform'/);
  assert.match(html, /Core\.pickUniformQuestion\(usable\)/);
  assert.match(html, /Core\.pickWeightedQuestion\(usable, state\.progress\)/);
});

test('paper view supports filtered exam generation and hides answers until complete submission', () => {
  assert.match(html, /data-view="paper"[^>]*>组卷<\/button>/);
  assert.match(html, /id="paper-view"/);
  assert.match(html, /id="paper-subject-filter"/);
  assert.match(html, /id="paper-type-filter"/);
  assert.match(html, /id="paper-weight-mode-filter"/);
  assert.match(html, /id="paper-count"/);
  assert.match(html, /id="generate-paper"/);
  assert.match(html, /id="submit-paper"/);
  assert.match(html, /function renderPaper\(\)/);
  assert.match(html, /function submitPaper\(\)/);
  assert.match(html, /Core\.selectPaperQuestions\(/);
  assert.match(html, /if \(!isPaperComplete\(\)\)/);
  assert.match(html, /if \(state\.paperSubmitted\) \{/);
});

test('series review view loads same-series data and does not write global progress', () => {
  assert.match(html, /data-view="series"[^>]*>专题复习<\/button>/);
  assert.match(html, /id="series-view"/);
  assert.match(html, /id="series-select"/);
  assert.match(html, /id="series-shuffle-options"/);
  assert.match(html, /id="start-series"/);
  assert.match(html, /id="series-submit-answer"/);
  assert.match(html, /const seriesBank = \(window\.SAME_SERIES_BANK \|\| \[\]\)/);
  assert.match(html, /function startSeriesReview\(\)/);
  assert.match(html, /function submitSeriesAnswer\(\)/);
  assert.match(html, /function renderSeriesQuestion\(\)/);
  assert.match(html, /Core\.pickUniformQuestion\(usable\)/);

  const submitSeriesBody = html.match(/function submitSeriesAnswer\(\) \{([\s\S]*?)\n\}/)?.[1] || '';
  assert.doesNotMatch(submitSeriesBody, /updateProgressAfterAnswer/);
  assert.doesNotMatch(submitSeriesBody, /state\.today\.count/);
  assert.doesNotMatch(submitSeriesBody, /saveProgress\(\)/);
});

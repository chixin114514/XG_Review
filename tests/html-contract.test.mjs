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

test('wrong book and favorites show options, paginate, and support direct review actions', () => {
  assert.match(html, /const LIST_PAGE_SIZE = 20;/);
  assert.match(html, /id="start-wrong-review"/);
  assert.match(html, /id="wrong-prev-page"/);
  assert.match(html, /id="wrong-next-page"/);
  assert.match(html, /id="wrong-page-status"/);
  assert.match(html, /id="start-favorite-review"/);
  assert.match(html, /id="favorite-prev-page"/);
  assert.match(html, /id="favorite-next-page"/);
  assert.match(html, /id="favorite-page-status"/);
  assert.match(html, /<div class="compact-options">\$\{renderQuestionOptionList\(item\.question\)\}<\/div>/);
  assert.match(html, /<p class="answer-line">\$\{renderQuestionAnswerLine\(item\.question\)\}<\/p>/);
  assert.match(html, /function startScopedReview\(scope\)/);
  assert.match(html, /function removeWrongQuestion\(questionId\)/);
  assert.match(html, /function removeFavoriteQuestion\(questionId\)/);
  assert.match(html, /wrongItems\.slice\(start, start \+ LIST_PAGE_SIZE\)/);
  assert.match(html, /favoriteItems\.slice\(start, start \+ LIST_PAGE_SIZE\)/);
  assert.match(html, /button\.className = 'danger-button';[\s\S]*?button\.textContent = '移出错题';/);
  assert.match(html, /button\.className = 'danger-button';[\s\S]*?button\.textContent = '取消收藏';/);
});

test('wrong book and favorites can add questions into a series review set', () => {
  assert.match(html, /const SERIES_ADDITIONS_KEY = 'xi-mao-review-series-additions-v1';/);
  assert.match(html, /id="current-series-target"/);
  assert.match(html, /id="add-current-to-series"/);
  assert.match(html, /function loadSeriesAdditions\(\)/);
  assert.match(html, /function saveSeriesAdditions\(\)/);
  assert.match(html, /function populatePracticeSeriesSelect\(\)/);
  assert.match(html, /function getSeriesTargetOptions\(\)/);
  assert.match(html, /function cloneQuestionForSeries\(question, seriesName, index\)/);
  assert.match(html, /function addQuestionToSeries\(question, seriesName\)/);
  assert.match(html, /class="series-target"/);
  assert.match(html, /button\.textContent = '加入专题';/);
  assert.match(html, /elements\.addCurrentToSeries\.addEventListener\('click'/);
  assert.match(html, /state\.seriesAdditions/);
  assert.match(html, /questions: \[\.\.\.series\.questions, \.\.\.additions\]/);
  assert.match(html, /saveCustomSeries\(\);[\s\S]*?saveSeriesAdditions\(\);/);
});

test('practice notes can be revealed before answering and edited after answering', () => {
  assert.match(html, /id="note-status"/);
  assert.match(html, /id="question-note"/);
  assert.match(html, /id="question-note-box"/);
  assert.match(html, /questionNote: document\.getElementById\('question-note'\),/);
  assert.match(html, /questionNoteBox: document\.getElementById\('question-note-box'\),/);
  assert.match(html, /noteStatus: document\.getElementById\('note-status'\),/);
  assert.match(html, /function renderQuestionNote\(\)/);
  assert.match(html, /function revealQuestionNote\(\)/);
  assert.match(html, /function saveQuestionNote\(\)/);
  assert.match(html, /elements\.questionNote\.disabled = !state\.answered;/);
  assert.match(html, /noteRevealed: false,/);
  assert.match(html, /state\.noteRevealed = false;/);
  assert.match(html, /state\.noteRevealed = true;/);
  assert.match(html, /state\.noteRevealed = true;[\s\S]*?saveProgress\(\);/);
  assert.match(html, /elements\.questionNote\.value = \(state\.answered \|\| state\.noteRevealed\) \? stats\.note \|\| '' : '';/);
  assert.match(html, /elements\.questionNoteBox\.classList\.toggle\('note-revealed', state\.answered \|\| state\.noteRevealed\);/);
  assert.doesNotMatch(html, /elements\.questionNoteBox\.classList\.toggle\('note-revealed', state\.answered\);/);
  assert.match(html, /elements\.questionNoteBox\.addEventListener\('dblclick', revealQuestionNote\);/);
  assert.match(html, /已显示笔记，提交答案后才能修改。/);
  assert.match(html, /可编辑当前题笔记。/);
  assert.match(html, /双击“笔记”标题或本卡片空白处查看笔记。/);
  assert.match(html, /note: elements\.questionNote\.value,/);
  assert.match(html, /if \(!state\.current \|\| !state\.answered\) return;/);
  assert.match(html, /elements\.questionNote\.addEventListener\('input', saveQuestionNote\);/);
});

test('search view can find questions and add results into a series', () => {
  assert.match(html, /data-view="search"[^>]*>搜题<\/button>/);
  assert.match(html, /id="search-view"/);
  assert.match(html, /id="question-search-query"/);
  assert.match(html, /id="question-search-button"/);
  assert.match(html, /id="question-search-results"/);
  assert.match(html, /id="question-search-summary"/);
  assert.match(html, /searchView: document\.getElementById\('search-view'\),/);
  assert.match(html, /questionSearchQuery: document\.getElementById\('question-search-query'\),/);
  assert.match(html, /questionSearchButton: document\.getElementById\('question-search-button'\),/);
  assert.match(html, /questionSearchResults: document\.getElementById\('question-search-results'\),/);
  assert.match(html, /questionSearchSummary: document\.getElementById\('question-search-summary'\),/);
  assert.match(html, /function renderQuestionSearchResults\(results = state\.questionSearchResults\)/);
  assert.match(html, /function runQuestionSearch\(\)/);
  assert.match(html, /Core\.searchQuestionBank\(questions, elements\.questionSearchQuery\.value, 80\)/);
  assert.match(html, /<div class="compact-options">\$\{renderQuestionOptionList\(question\)\}<\/div>/);
  assert.match(html, /<p class="answer-line">\$\{renderQuestionAnswerLine\(question\)\}<\/p>/);
  assert.match(html, /appendSeriesAddControls\(row, question\);/);
  assert.match(html, /if \(isSearch\) renderQuestionSearchResults\(\);/);
});

test('search, wrong book, and favorites show correct answers in list views', () => {
  assert.match(html, /function renderQuestionAnswerLine\(question\)/);
  assert.match(html, /标准答案：\$\{answerKeys\}/);
  assert.match(html, /答案内容：\$\{answerValues\}/);
  assert.match(html, /renderQuestionSearchResults[\s\S]*?<p class="answer-line">\$\{renderQuestionAnswerLine\(question\)\}<\/p>/);
  assert.match(html, /renderWrongBook[\s\S]*?<p class="answer-line">\$\{renderQuestionAnswerLine\(item\.question\)\}<\/p>/);
  assert.match(html, /renderFavoriteBook[\s\S]*?<p class="answer-line">\$\{renderQuestionAnswerLine\(item\.question\)\}<\/p>/);
});

test('progress import and export use a complete backup with merge support', () => {
  assert.match(html, /id="import-mode"/);
  assert.match(html, /<option value="merge">合并导入<\/option>/);
  assert.match(html, /<option value="replace">覆盖导入<\/option>/);
  assert.match(html, /id="storage-status"/);
  assert.match(html, /version: 2,/);
  assert.match(html, /customSeries: state\.customSeries,/);
  assert.match(html, /seriesAdditions: state\.seriesAdditions,/);
  assert.match(html, /today: state\.today,/);
  assert.match(html, /function normalizeBackupPayload\(payload\)/);
  assert.match(html, /function mergeProgress\(currentProgress, incomingProgress\)/);
  assert.match(html, /function mergeCustomSeries\(currentSeries, incomingSeries\)/);
  assert.match(html, /function mergeSeriesAdditions\(currentAdditions, incomingAdditions\)/);
  assert.match(html, /function applyBackup\(backup, mode\)/);
  assert.match(html, /const mode = elements\.importMode\.value;/);
  assert.match(html, /state\.customSeries = mode === 'replace'/);
  assert.match(html, /saveCustomSeries\(\);/);
  assert.match(html, /saveSeriesAdditions\(\);/);
  assert.match(html, /saveToday\(\);/);
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

test('practice scope can target same-series review sets', () => {
  assert.match(html, /function populatePracticeScopeSelect\(\)/);
  assert.match(html, /function getSeriesScopeValue\(seriesName\)/);
  assert.match(html, /return `series:\$\{seriesName\}`;/);
  assert.match(html, /option\.textContent = `专题：\$\{label\}（\$\{series\.questions\.length\} 题）`;/);
  assert.match(html, /elements\.scopeFilter\.appendChild\(option\);/);
  assert.match(html, /if \(scope\.startsWith\('series:'\)\)/);
  assert.match(html, /const selectedSeries = getSeriesByScopeValue\(scope\);/);
  assert.match(html, /sourceQuestions = selectedSeries \? selectedSeries\.questions\.map\(normalizePracticeQuestion\) : \[\];/);
  assert.match(html, /const candidates = getFilteredQuestions\(\);[\s\S]*?Core\.takePreviousQuestion\(candidates, state\.history\)/);
  assert.match(html, /populatePracticeScopeSelect\(\);/);
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

test('series view can build custom series from question bank search', () => {
  assert.match(html, /id="custom-series-name"/);
  assert.match(html, /id="series-search-query"/);
  assert.match(html, /id="series-search-button"/);
  assert.match(html, /id="series-search-results"/);
  assert.match(html, /id="custom-series-selected-list"/);
  assert.match(html, /id="save-custom-series"/);
  assert.match(html, /CUSTOM_SERIES_KEY/);
  assert.match(html, /function loadCustomSeries\(\)/);
  assert.match(html, /function getAllSeries\(\)/);
  assert.match(html, /function renderQuestionOptionList\(question\)/);
  assert.match(html, /function searchSeriesQuestions\(\)/);
  assert.match(html, /function saveCustomSeriesDraft\(\)/);
  assert.match(html, /<div class="compact-options">\$\{renderQuestionOptionList\(question\)\}<\/div>/);
  assert.match(html, /Core\.searchQuestionBank\(questions, elements\.seriesSearchQuery\.value/);
});

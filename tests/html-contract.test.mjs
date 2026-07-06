import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');

test('submit button turns into the next question action after submission', () => {
  assert.doesNotMatch(html, /id="next-question"/);
  assert.match(html, /elements\.submitAnswer\.textContent = '提交';/);
  assert.match(html, /elements\.submitAnswer\.textContent = '下一题';/);
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

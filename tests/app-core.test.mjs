import test from 'node:test';
import assert from 'node:assert/strict';

import {
  getSubjectLabel,
  getQuestionType,
  normalizeAnswer,
  isCorrectAnswer,
  canSubmitAnswer,
  getQuestionStats,
  getQuestionWeight,
  buildWeightedPool,
  pickWeightedQuestion,
  rememberQuestion,
  getDisplayedCorrectAnswer,
  shuffleOptionValues,
  takePreviousQuestion,
} from '../src/app-core.mjs';

const sampleQuestions = [
  {
    id: 0,
    category: 'X',
    question: '单选题',
    options: { A: '一', B: '二', C: '三', D: '四' },
    correct_answer: ['A'],
  },
  {
    id: 1,
    category: 'M',
    question: '多选题',
    options: { A: '一', B: '二', C: '三', D: '四' },
    correct_answer: ['A', 'C'],
  },
  {
    id: 2,
    category: 'M',
    question: '判断题',
    options: { A: 'True', B: 'False' },
    correct_answer: ['B'],
  },
];

test('maps X and M categories to visible subject labels', () => {
  assert.equal(getSubjectLabel('X'), '习概');
  assert.equal(getSubjectLabel('M'), '毛概');
  assert.equal(getSubjectLabel('unknown'), '未分类');
});

test('classifies single choice, multiple choice, and true false questions', () => {
  assert.equal(getQuestionType(sampleQuestions[0]), 'single');
  assert.equal(getQuestionType(sampleQuestions[1]), 'multiple');
  assert.equal(getQuestionType(sampleQuestions[2]), 'truefalse');
});

test('normalizes selected answers before comparing', () => {
  assert.deepEqual(normalizeAnswer(['C', 'A', 'A']), ['A', 'C']);
  assert.equal(isCorrectAnswer(['C', 'A'], ['A', 'C']), true);
  assert.equal(isCorrectAnswer(['A'], ['A', 'C']), false);
  assert.equal(isCorrectAnswer(['A', 'B', 'C'], ['A', 'C']), false);
});

test('requires at least two selections for multiple choice submissions', () => {
  assert.equal(canSubmitAnswer(sampleQuestions[0], ['A']).ok, true);
  assert.equal(canSubmitAnswer(sampleQuestions[1], ['A']).ok, false);
  assert.equal(canSubmitAnswer(sampleQuestions[1], ['A', 'C']).ok, true);
});

test('uses base weight plus capped mistake weight and lowers mastered questions', () => {
  assert.equal(getQuestionWeight({ wrongCount: 0, mastered: false }), 1);
  assert.equal(getQuestionWeight({ wrongCount: 1, mastered: false }), 3);
  assert.equal(getQuestionWeight({ wrongCount: 9, mastered: false }), 11);
  assert.equal(getQuestionWeight({ wrongCount: 4, mastered: true }), 2);
});

test('builds a weighted pool while preserving every question baseline presence', () => {
  const progress = {
    '0': { wrongCount: 0, mastered: false },
    '1': { wrongCount: 3, mastered: false },
    '2': { wrongCount: 0, mastered: false },
  };
  const pool = buildWeightedPool(sampleQuestions, progress);
  const counts = pool.reduce((acc, id) => {
    acc[id] = (acc[id] || 0) + 1;
    return acc;
  }, {});

  assert.equal(counts[0], 1);
  assert.equal(counts[1], 7);
  assert.equal(counts[2], 1);
});

test('picks from the weighted pool deterministically when random value is injected', () => {
  const progress = {
    '0': { wrongCount: 0, mastered: false },
    '1': { wrongCount: 2, mastered: false },
    '2': { wrongCount: 0, mastered: false },
  };

  assert.equal(pickWeightedQuestion(sampleQuestions, progress, () => 0).id, 0);
  assert.equal(pickWeightedQuestion(sampleQuestions, progress, () => 0.2).id, 1);
  assert.equal(pickWeightedQuestion(sampleQuestions, progress, () => 0.99).id, 2);
});

test('returns default stats for unseen questions', () => {
  assert.deepEqual(getQuestionStats({}, 42), {
    seenCount: 0,
    correctCount: 0,
    wrongCount: 0,
    streak: 0,
    mastered: false,
    favorite: false,
    lastAnsweredAt: null,
  });
});

test('records and restores previous question history without duplicating current question', () => {
  assert.deepEqual(rememberQuestion([], 0, 1), [0]);
  assert.deepEqual(rememberQuestion([0], 1, 1), [0]);

  const restored = takePreviousQuestion(sampleQuestions, [0, 1]);
  assert.equal(restored.question.id, 1);
  assert.deepEqual(restored.history, [0]);

  const empty = takePreviousQuestion(sampleQuestions, []);
  assert.equal(empty.question, null);
  assert.deepEqual(empty.history, []);
});

test('shuffles option values while keeping visible option labels fixed', () => {
  const entries = Object.entries(sampleQuestions[0].options);
  const randomValues = [0.1, 0.8, 0.3];
  const displayed = shuffleOptionValues(entries, () => randomValues.shift());

  assert.deepEqual(displayed.map(([key]) => key), ['A', 'B', 'C', 'D']);
  assert.deepEqual(displayed.map(([, value]) => value), ['二', '四', '三', '一']);
  assert.deepEqual(displayed.map(([, , originalKey]) => originalKey), ['B', 'D', 'C', 'A']);
  assert.deepEqual(entries.map(([key]) => key), ['A', 'B', 'C', 'D']);
});

test('remaps correct answers to the displayed label after option values move', () => {
  const displayed = [
    ['A', '二', 'B'],
    ['B', '四', 'D'],
    ['C', '三', 'C'],
    ['D', '一', 'A'],
  ];

  assert.deepEqual(getDisplayedCorrectAnswer(displayed, ['A']), ['D']);
  assert.deepEqual(getDisplayedCorrectAnswer(displayed, ['A', 'C']), ['C', 'D']);
});

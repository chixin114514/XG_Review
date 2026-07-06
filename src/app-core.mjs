export const DEFAULT_STATS = Object.freeze({
  seenCount: 0,
  correctCount: 0,
  wrongCount: 0,
  streak: 0,
  mastered: false,
  favorite: false,
  lastAnsweredAt: null,
});

export function getSubjectLabel(category) {
  if (category === 'X') return '习概';
  if (category === 'M') return '毛概';
  return '未分类';
}

export function getQuestionType(question) {
  const answers = question.correct_answer || [];
  const options = question.options || {};
  const values = Object.values(options).map((value) => String(value).toLowerCase());

  if (
    Object.keys(options).length === 2 &&
    values.includes('true') &&
    values.includes('false')
  ) {
    return 'truefalse';
  }

  return answers.length > 1 ? 'multiple' : 'single';
}

export function getQuestionTypeLabel(type) {
  if (type === 'multiple') return '多选';
  if (type === 'truefalse') return '判断';
  return '单选';
}

export function normalizeAnswer(answer) {
  return [...new Set(answer)].sort();
}

export function isCorrectAnswer(selected, correct) {
  const normalizedSelected = normalizeAnswer(selected);
  const normalizedCorrect = normalizeAnswer(correct);

  if (normalizedSelected.length !== normalizedCorrect.length) return false;
  return normalizedSelected.every((item, index) => item === normalizedCorrect[index]);
}

export function canSubmitAnswer(question, selected) {
  const normalizedSelected = normalizeAnswer(selected);
  if (normalizedSelected.length === 0) {
    return { ok: false, message: '先选择答案。' };
  }

  if (getQuestionType(question) === 'multiple' && normalizedSelected.length < 2) {
    return { ok: false, message: '多选题至少选择两个选项。' };
  }

  return { ok: true, message: '' };
}

export function getQuestionStats(progress, questionId) {
  return {
    ...DEFAULT_STATS,
    ...(progress[String(questionId)] || {}),
  };
}

export function getQuestionWeight(stats) {
  const baseWeight = 1 + Math.min(stats.wrongCount || 0, 5) * 2;

  if (stats.mastered) {
    return Math.max(1, Math.floor(baseWeight / 4));
  }

  return baseWeight;
}

export function buildWeightedPool(questions, progress) {
  const pool = [];

  for (const question of questions) {
    const stats = getQuestionStats(progress, question.id);
    const weight = getQuestionWeight(stats);
    for (let index = 0; index < weight; index += 1) {
      pool.push(question.id);
    }
  }

  return pool;
}

export function pickWeightedQuestion(questions, progress, random = Math.random) {
  if (!questions.length) return null;

  const pool = buildWeightedPool(questions, progress);
  const pickedId = pool[Math.min(pool.length - 1, Math.floor(random() * pool.length))];

  return questions.find((question) => question.id === pickedId) || questions[0];
}

export function rememberQuestion(history, currentId, nextId, maxLength = 100) {
  if (currentId === null || currentId === undefined || currentId === nextId) {
    return history;
  }

  return [...history, currentId].slice(-maxLength);
}

export function takePreviousQuestion(questions, history) {
  if (!history.length) {
    return { question: null, history: [] };
  }

  const nextHistory = history.slice(0, -1);
  const previousId = history[history.length - 1];
  const question = questions.find((item) => item.id === previousId) || null;

  return { question, history: nextHistory };
}

export function updateProgressAfterAnswer(progress, questionId, wasCorrect, now = new Date()) {
  const id = String(questionId);
  const previous = getQuestionStats(progress, id);
  const next = {
    ...previous,
    seenCount: previous.seenCount + 1,
    correctCount: previous.correctCount + (wasCorrect ? 1 : 0),
    wrongCount: previous.wrongCount + (wasCorrect ? 0 : 1),
    streak: wasCorrect ? previous.streak + 1 : 0,
    lastAnsweredAt: now.toISOString(),
  };

  next.mastered = next.wrongCount > 0 && next.streak >= 2;

  return {
    ...progress,
    [id]: next,
  };
}

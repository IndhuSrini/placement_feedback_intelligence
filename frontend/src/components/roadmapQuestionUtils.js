export function normalizeId(value) {
  return value === null || value === undefined || value === ""
    ? null
    : String(value);
}

export function normalizeQuestionText(value) {
  return String(value || "")
    .replace(/\*\*/g, "")
    .replace(/__/g, "")
    .replace(/^["']|["']$/g, "")
    .replace(/^\d+[.)]\s*/, "")
    .trim();
}

export function questionKey(question) {
  const text = normalizeQuestionText(
    question.question || question.question_text
  );
  return text.toLowerCase().replace(/[^a-z0-9]/g, "");
}

export function uniqueQuestions(questions) {
  const questionsByContext = new Map();

  for (const question of questions) {
    if (!questionKey(question)) continue;

    const key = JSON.stringify([
      questionKey(question),
      normalizeId(question.round_id),
      normalizeId(question.topic_id),
      String(question.topic_category || "").trim().toLowerCase(),
    ]);
    if (!questionsByContext.has(key)) questionsByContext.set(key, question);
  }

  return Array.from(questionsByContext.values());
}

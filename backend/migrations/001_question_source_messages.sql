CREATE TABLE IF NOT EXISTS question_source_messages (
    question_id INTEGER NOT NULL REFERENCES questions(id),
    raw_message_id INTEGER NOT NULL REFERENCES raw_messages(id),
    PRIMARY KEY (question_id, raw_message_id)
);

INSERT INTO question_source_messages (question_id, raw_message_id)
SELECT questions.id, questions.source_message_id
FROM questions
WHERE questions.source_message_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM question_source_messages
      WHERE question_source_messages.question_id = questions.id
        AND question_source_messages.raw_message_id = questions.source_message_id
  );

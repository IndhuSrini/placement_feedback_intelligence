import { describe, expect, it } from "vitest";
import { uniqueQuestions } from "./roadmapQuestionUtils";

describe("uniqueQuestions", () => {
  it("removes repeated question text within the same round and topic", () => {
    const questions = [
      {
        question: "What is normalization in DBMS?",
        round_id: 1,
        topic_id: 2,
        topic_category: "Technical",
      },
      {
        question: "what is normalization in dbms",
        round_id: "1",
        topic_id: "2",
        topic_category: "technical",
      },
    ];

    expect(uniqueQuestions(questions)).toHaveLength(1);
  });

  it("keeps identical question text with different round or topic associations", () => {
    const questions = [
      {
        question: "Explain arrays",
        round_id: 1,
        topic_id: 2,
        topic_category: "Coding",
      },
      {
        question: "Explain arrays",
        round_id: 2,
        topic_id: 3,
        topic_category: "Technical",
      },
    ];

    expect(uniqueQuestions(questions)).toEqual(questions);
  });
});

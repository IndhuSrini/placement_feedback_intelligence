import { useMemo, useRef, useState } from "react";
import {
  ArrowDown,
  Award,
  BookOpenCheck,
  BriefcaseBusiness,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  GraduationCap,
  RotateCcw,
  Sparkles,
  Target,
  Trophy,
  ListChecks,
  MessageSquareText,
} from "lucide-react";
import {
  normalizeId,
  normalizeQuestionText,
  questionKey,
  uniqueQuestions,
} from "./roadmapQuestionUtils";
import "./InterviewPreparationRoadmap.css";

function topicChecklistKey(round, topic) {
  const roundId = normalizeId(round.id) || `round-${round.sourceIndex}`;
  const topicId =
    normalizeId(topic.id ?? topic.topic_id) ||
    `topic-${topic.topic || topic.name}`;
  return `topic:${roundId}:${topicId}`;
}

function questionChecklistKey(question) {
  return normalizeId(question.id) !== null
    ? `question:${normalizeId(question.id)}`
    : `question-text:${questionKey(question)}`;
}

function topicContextKey(topic) {
  const topicId = normalizeId(topic.id ?? topic.topic_id);
  const category = String(topic.category || "").trim().toLowerCase();
  return topicId === null
    ? `topic:${topic.topic || topic.name}:${category}`
    : `${topicId}:${category}`;
}

function difficultyClass(value) {
  const difficulty = String(value || "").toLowerCase();
  if (difficulty.includes("easy")) return "easy";
  if (difficulty.includes("hard") || difficulty.includes("difficult")) {
    return "hard";
  }
  if (difficulty.includes("medium") || difficulty.includes("moderate")) {
    return "medium";
  }
  return "other";
}

function RoadmapQuestion({
  question,
  topic,
  itemKey,
  completed,
  needsReview,
  onToggle,
  onReview,
}) {
  const questionText = normalizeQuestionText(
    question.question || question.question_text
  );
  const hasAdditionalDetails =
    question.confidence_score !== null &&
    question.confidence_score !== undefined ||
    Boolean(question.verification_status) ||
    (question.source_message_id !== null &&
      question.source_message_id !== undefined);

  return (
    <article
      className={`roadmap-question-item${completed ? " is-complete" : ""}${needsReview ? " needs-review" : ""}`}
    >
      <label className="roadmap-question-check">
        <input
          type="checkbox"
          checked={completed}
          onChange={(event) => onToggle(itemKey, event.target.checked)}
          aria-label={`Mark question as practised: ${questionText}`}
        />
        <span className="roadmap-checkmark">
          <CheckCircle2 size={16} />
        </span>
      </label>
      <div className="roadmap-question-body">
        <p>{questionText}</p>
        <div className="roadmap-question-meta">
          {question.occurrence_count !== null &&
            question.occurrence_count !== undefined && (
              <span>
                Reported {question.occurrence_count} time
                {Number(question.occurrence_count) === 1 ? "" : "s"}
              </span>
            )}
          {question.difficulty && (
            <span
              className={`roadmap-difficulty ${difficultyClass(question.difficulty)}`}
            >
              {question.difficulty}
            </span>
          )}
          {topic ? (
            <span className="roadmap-topic-reference">
              {topic.topic || topic.name}
            </span>
          ) : (
            <span className="roadmap-unlinked-label">No topic linked</span>
          )}
        </div>
        {hasAdditionalDetails && (
          <details className="roadmap-question-details">
            <summary>Question details</summary>
            <div>
              {typeof question.confidence_score === "number" && (
                <span>{Math.round(question.confidence_score)}% confidence</span>
              )}
              {question.verification_status && (
                <span
                  className={
                    question.verification_status === "verified"
                      ? "roadmap-verified"
                      : "roadmap-unverified"
                  }
                >
                  {question.verification_status === "verified"
                    ? "Verified"
                    : question.verification_status}
                </span>
              )}
              {question.source_message_id !== null &&
                question.source_message_id !== undefined && (
                  <span>Source message {question.source_message_id}</span>
                )}
            </div>
          </details>
        )}
        <button
          type="button"
          className={`roadmap-review-toggle${needsReview ? " is-active" : ""}`}
          onClick={() => onReview(itemKey, !needsReview)}
          aria-pressed={needsReview}
        >
          <RotateCcw size={13} />
          {needsReview ? "Marked for review" : "Mark for review"}
        </button>
      </div>
    </article>
  );
}

function RoadmapTopic({
  topic,
  itemKey,
  completed,
  needsReview,
  onToggle,
  onReview,
  relatedQuestionCount = 0,
}) {
  const topicName = topic.topic || topic.name;

  return (
    <div
      className={`roadmap-topic-entry${completed ? " is-complete" : ""}${needsReview ? " needs-review" : ""}`}
    >
      <label className="roadmap-topic-item">
        <input
          type="checkbox"
          checked={completed}
          onChange={(event) => onToggle(itemKey, event.target.checked)}
          aria-label={`Mark topic as completed: ${topicName}`}
        />
        <span className="roadmap-checkmark">
          <CheckCircle2 size={16} />
        </span>
        <span className="roadmap-topic-text">
          <strong>{topicName}</strong>
          {topic.category && <small>{topic.category}</small>}
          <small className="roadmap-learning-status">
            {needsReview ? "Needs review" : completed ? "Completed" : "To learn"}
          </small>
        </span>
        {topic.occurrence_count !== null &&
          topic.occurrence_count !== undefined && (
            <span className="roadmap-frequency">
              {topic.occurrence_count} mention
              {Number(topic.occurrence_count) === 1 ? "" : "s"}
            </span>
          )}
        {relatedQuestionCount > 0 && (
          <span className="roadmap-topic-question-count">
            {relatedQuestionCount} question{relatedQuestionCount === 1 ? "" : "s"}
          </span>
        )}
      </label>
      <button
        type="button"
        className={`roadmap-topic-review${needsReview ? " is-active" : ""}`}
        onClick={() => onReview(itemKey, !needsReview)}
        aria-label={`${needsReview ? "Remove review flag from" : "Mark"} ${topicName} ${needsReview ? "" : "for review"}`}
        aria-pressed={needsReview}
      >
        <RotateCcw size={13} />
      </button>
    </div>
  );
}

function InterviewPreparationRoadmap({
  companyId,
  driveId,
  companyName,
  jobRole,
  rounds: rawRounds,
  topics: rawTopics,
  preparationTopics: rawPreparationTopics,
  questions: rawQuestions,
  eligibility,
}) {
  const storageKey = `placement-feedback-intelligence:roadmap:${companyId}:${driveId ?? "none"}`;
  const [progressState, setProgressState] = useState(() => {
    try {
      const saved = window.localStorage.getItem(storageKey);
      const parsed = saved ? JSON.parse(saved) : {};
      const savedItems =
        parsed && typeof parsed === "object" && !Array.isArray(parsed)
          ? parsed.completedItems ?? parsed.items ?? parsed
          : {};
      return {
        items:
          savedItems && typeof savedItems === "object" && !Array.isArray(savedItems)
            ? Object.fromEntries(
                Object.entries(savedItems).map(([key, value]) => [
                  key,
                  value === true || value?.completed === true,
                ])
              )
            : {},
        reviews:
          parsed && typeof parsed === "object" && !Array.isArray(parsed)
            ? parsed.reviewItems || {}
            : {},
        error: "",
      };
    } catch (error) {
      console.error("Could not load interview roadmap progress:", error);
      return {
        items: {},
        reviews: {},
        error: "Progress could not be loaded from this browser.",
      };
    }
  });
  const completedItems = progressState.items;
  const reviewItems = progressState.reviews;
  const [expandedRoundId, setExpandedRoundId] = useState(null);
  const [difficultyFilters, setDifficultyFilters] = useState({});
  const roundRefs = useRef({});
  const eligibilityRef = useRef(null);
  const additionalPreparationRef = useRef(null);
  const reviewRef = useRef(null);

  const roadmapRounds = useMemo(() => {
    if (!Array.isArray(rawRounds)) return [];

    const roundsByMeaning = new Map();
    rawRounds
      .filter((round) => round && typeof round === "object")
      .map((round, index) => ({ ...round, sourceIndex: index }))
      .forEach((round) => {
        const roundType = String(round.round_type || "").toLowerCase();
        const descriptionKey = String(round.description || "")
          .toLowerCase()
          .replace(/\b(round|interview|stage|assessment)\b/g, " ")
          .replace(/[^a-z0-9]+/g, " ")
          .trim();
        const meaning = `${roundType}|${
          descriptionKey ||
          `round:${round.round_number ?? round.sourceIndex}`
        }`;
        const existing = roundsByMeaning.get(meaning);
        const roundNumber = Number(round.round_number);
        const existingNumber = Number(existing?.round_number);
        if (
          !existing ||
          (Number.isFinite(roundNumber) &&
            roundNumber > 0 &&
            (!Number.isFinite(existingNumber) ||
              existingNumber <= 0 ||
              roundNumber < existingNumber))
        ) {
          roundsByMeaning.set(meaning, round);
        }
      });

    return Array.from(roundsByMeaning.values())
      .sort((left, right) => {
        const leftNumber = Number(left.round_number);
        const rightNumber = Number(right.round_number);
        const leftHasNumber = Number.isFinite(leftNumber) && leftNumber > 0;
        const rightHasNumber = Number.isFinite(rightNumber) && rightNumber > 0;

        if (leftHasNumber && rightHasNumber) {
          return leftNumber - rightNumber || left.sourceIndex - right.sourceIndex;
        }
        if (leftHasNumber) return -1;
        if (rightHasNumber) return 1;
        return left.sourceIndex - right.sourceIndex;
      });
  }, [rawRounds]);

  const preparationTopics = useMemo(
    () =>
      (Array.isArray(rawPreparationTopics) ? rawPreparationTopics : []).filter(
        (topic) => topic && (topic.topic || topic.name)
      ),
    [rawPreparationTopics]
  );

  const topics = useMemo(() => {
    const byContext = new Map();
    const unkeyed = [];

    for (const topic of [
      ...(Array.isArray(rawTopics) ? rawTopics : []),
      ...preparationTopics,
    ]) {
      if (!topic || !(topic.topic || topic.name)) continue;
      const topicId = normalizeId(topic.id ?? topic.topic_id);
      const normalized = {
        ...topic,
        id: topic.id ?? topic.topic_id,
        topic: topic.topic || topic.name,
      };

      if (topicId === null) {
        unkeyed.push(normalized);
      } else {
        const key = topicContextKey(normalized);
        byContext.set(key, { ...byContext.get(key), ...normalized });
      }
    }

    return [...byContext.values(), ...unkeyed];
  }, [rawTopics, preparationTopics]);

  const questions = useMemo(
    () =>
      (Array.isArray(rawQuestions) ? rawQuestions : []).filter(
        (question) =>
          question &&
          normalizeQuestionText(question.question || question.question_text)
      ),
    [rawQuestions]
  );

  const topicById = useMemo(
    () =>
      new Map(
        topics
          .map((topic) => [normalizeId(topic.id), topic])
          .filter(([id]) => id !== null)
      ),
    [topics]
  );

  const roadmap = useMemo(() => {
    const knownRoundIds = new Set(
      roadmapRounds
        .map((round) => normalizeId(round.id))
        .filter((id) => id !== null)
    );
    const assignedTopicIds = new Set();
    const distinctQuestions = uniqueQuestions(questions);

    const rounds = roadmapRounds.map((round, index) => {
      const roundId = normalizeId(round.id);
      const linkedQuestions = distinctQuestions.filter(
        (question) =>
          roundId !== null && normalizeId(question.round_id) === roundId
      );
      const roundTopicsByContext = new Map();

      preparationTopics
        .filter(
          (topic) =>
            roundId !== null && normalizeId(topic.round_id) === roundId
        )
        .forEach((topic) => {
          const topicId = normalizeId(topic.id ?? topic.topic_id);
          if (topicId !== null) {
            roundTopicsByContext.set(topicContextKey(topic), topic);
          }
        });

      linkedQuestions.forEach((question) => {
        const topicId = normalizeId(question.topic_id);
        const topic = topicById.get(topicId);
        if (topicId !== null && topic) {
          const questionTopic = {
            ...topic,
            round_id: round.id,
            category: question.topic_category || topic.category,
          };
          roundTopicsByContext.set(topicContextKey(questionTopic), questionTopic);
        }
      });

      const roundTopics = Array.from(roundTopicsByContext.values());
      roundTopics.forEach((topic) => {
        const topicId = normalizeId(topic.id ?? topic.topic_id);
        if (topicId !== null) assignedTopicIds.add(topicId);
      });

      return {
        ...round,
        displayNumber:
          round.round_number !== null &&
          round.round_number !== undefined &&
          round.round_number !== ""
            ? round.round_number
            : index + 1,
        topics: roundTopics,
        questions: linkedQuestions,
      };
    });

    const standaloneTopicsByContext = new Map();
    preparationTopics
      .filter((topic) => normalizeId(topic.round_id) === null)
      .forEach((topic) => {
        const topicId = normalizeId(topic.id ?? topic.topic_id);
      const contextKey = topicContextKey(topic);
      if (topicId !== null && !standaloneTopicsByContext.has(contextKey)) {
        standaloneTopicsByContext.set(contextKey, topic);
      }
      if (topicId !== null) assignedTopicIds.add(topicId);
      });
    const standaloneTopics = Array.from(standaloneTopicsByContext.values());
    const standaloneTopicIds = new Set(
      standaloneTopics.map((topic) => normalizeId(topic.id ?? topic.topic_id))
    );
    const standaloneTechnicalTopics = standaloneTopics.filter(
      (topic) => String(topic.category || "").toLowerCase() === "technical"
    );
    const standaloneOtherTopics = standaloneTopics.filter(
      (topic) => String(topic.category || "").toLowerCase() !== "technical"
    );
    const standaloneQuestions = distinctQuestions.filter(
      (question) =>
        normalizeId(question.round_id) === null &&
        standaloneTopicIds.has(normalizeId(question.topic_id))
    );
    const standaloneCategory = (question) =>
      String(
        question.topic_category ||
          topicById.get(normalizeId(question.topic_id))?.category ||
          ""
      ).toLowerCase();
    const standaloneTechnicalQuestions = standaloneQuestions.filter(
      (question) => standaloneCategory(question) === "technical"
    );
    const standaloneOtherQuestions = standaloneQuestions.filter(
      (question) => {
        const category = standaloneCategory(question);
        return category !== "" && category !== "technical";
      }
    );
    const unclassifiedStandaloneQuestions = standaloneQuestions.filter(
      (question) => !standaloneCategory(question)
    );
    const unassignedQuestions = distinctQuestions.filter((question) => {
      const roundId = normalizeId(question.round_id);
      if (roundId !== null && !knownRoundIds.has(roundId)) return true;
      if (roundId !== null) return false;
      return (
        !standaloneTopicIds.has(normalizeId(question.topic_id)) ||
        unclassifiedStandaloneQuestions.includes(question)
      );
    });

    return {
      rounds,
      standaloneTopics,
      standaloneQuestions,
      standaloneOtherTopics,
      standaloneOtherQuestions,
      standaloneTechnicalTopics,
      standaloneTechnicalQuestions,
      unassignedTopics: topics.filter((topic) => {
        const topicId = normalizeId(topic.id ?? topic.topic_id);
        const hasUsablePreparationAssociation = preparationTopics.some(
          (preparedTopic) => {
            const preparedTopicId = normalizeId(
              preparedTopic.id ?? preparedTopic.topic_id
            );
            const roundId = normalizeId(preparedTopic.round_id);
            return (
              preparedTopicId === topicId &&
              (roundId === null || knownRoundIds.has(roundId))
            );
          }
        );
        return (
          topicId === null ||
          (!assignedTopicIds.has(topicId) &&
            !hasUsablePreparationAssociation)
        );
      }),
      unassignedQuestions,
    };
  }, [roadmapRounds, topics, questions, topicById, preparationTopics]);

  const eligibilityItems = Object.entries(eligibility || {}).filter(
    ([, value]) => value !== null && value !== undefined && String(value).trim()
  );
  const standaloneKey = (topic) =>
    topicChecklistKey(
      {
        id:
          String(topic.category || "").toLowerCase() === "technical"
            ? "technical-preparation"
            : "standalone-preparation",
      },
      topic
    );
  const checklistItems = [
    ...roadmap.rounds.flatMap((round) => [
      ...round.topics.map((topic) => ({
        key: topicChecklistKey(round, topic),
        label: topic.topic || topic.name,
        type: "Topic",
        section: round.round_type || `Round ${round.displayNumber}`,
      })),
      ...round.questions.map((question) => ({
        key: questionChecklistKey(question),
        label: normalizeQuestionText(question.question || question.question_text),
        type: "Question",
        section: round.round_type || `Round ${round.displayNumber}`,
      })),
    ]),
    ...roadmap.standaloneTopics.map((topic) => ({
      key: standaloneKey(topic),
      label: topic.topic || topic.name,
      type: "Topic",
      section: `${topic.category || "Additional"} preparation`,
    })),
    ...roadmap.standaloneQuestions.map((question) => ({
      key: questionChecklistKey(question),
      label: normalizeQuestionText(question.question || question.question_text),
      type: "Question",
      section: "Additional preparation",
    })),
    ...roadmap.unassignedTopics.map((topic) => ({
      key: topicChecklistKey({ id: "unassigned" }, topic),
      label: topic.topic || topic.name,
      type: "Topic",
      section: "Unassigned",
    })),
    ...roadmap.unassignedQuestions.map((question) => ({
      key: questionChecklistKey(question),
      label: normalizeQuestionText(question.question || question.question_text),
      type: "Question",
      section: "Unassigned",
    })),
    ...eligibilityItems.map(([key, value]) => ({
      key: `eligibility:${driveId ?? "none"}:${key}`,
      label: `${key.replaceAll("_", " ")}: ${value}`,
      type: "Eligibility",
      section: "Before you begin",
    })),
  ];
  const uniqueChecklistItems = Array.from(
    new Map(checklistItems.map((item) => [item.key, item])).values()
  );
  const pendingEligibility = eligibilityItems.filter(
    ([key]) => !completedItems[`eligibility:${driveId ?? "none"}:${key}`]
  );
  const checklistCount = uniqueChecklistItems.length;
  const completedCount = uniqueChecklistItems.filter(
    (item) => completedItems[item.key]
  ).length;
  const topicItems = uniqueChecklistItems.filter((item) => item.type === "Topic");
  const questionItems = uniqueChecklistItems.filter(
    (item) => item.type === "Question"
  );
  const completedTopicCount = topicItems.filter(
    (item) => completedItems[item.key]
  ).length;
  const remainingTopicCount = topicItems.length - completedTopicCount;
  const progress = checklistCount
    ? Math.round((completedCount / checklistCount) * 100)
    : 0;
  const reviewCount = uniqueChecklistItems.filter(
    (item) => reviewItems[item.key]
  ).length;
  const incompleteRounds = roadmap.rounds.filter((round) => {
    const roundKeys = [
      ...round.topics.map((topic) => topicChecklistKey(round, topic)),
      ...round.questions.map(questionChecklistKey),
    ];
    return roundKeys.some((key) => !completedItems[key] || reviewItems[key]);
  });
  const nextRound = incompleteRounds[0];
  const technicalItems = uniqueChecklistItems.filter(
    (item) => /technical/i.test(item.section)
  );
  const milestones = [
    {
      label: "First activity completed",
      earned: completedCount > 0,
    },
    {
      label: "First round complete",
      earned: roadmap.rounds.some((round) => {
        const keys = [
          ...round.topics.map((topic) => topicChecklistKey(round, topic)),
          ...round.questions.map(questionChecklistKey),
        ];
        return keys.length > 0 && keys.every((key) => completedItems[key]);
      }),
    },
    { label: "Halfway there", earned: progress >= 50 },
    {
      label: "Technical preparation complete",
      earned:
        technicalItems.length > 0 &&
        technicalItems.every((item) => completedItems[item.key]),
    },
    { label: "Roadmap complete", earned: checklistCount > 0 && progress === 100 },
  ].filter((milestone) => milestone.earned);

  function persistProgress(items, reviews) {
    try {
      window.localStorage.setItem(
        storageKey,
        JSON.stringify({ completedItems: items, reviewItems: reviews })
      );
      setProgressState({ items, reviews, error: "" });
    } catch (error) {
      console.error("Could not save interview roadmap progress:", error);
      setProgressState({
        items,
        reviews,
        error: "Progress could not be saved in this browser.",
      });
    }
  }

  function updateCompletion(itemKey, isComplete) {
    const updatedItems = {
      ...completedItems,
      [itemKey]: isComplete,
    };
    persistProgress(updatedItems, reviewItems);
  }

  function updateReview(itemKey, needsReview) {
    const updatedReviews = {
      ...reviewItems,
      [itemKey]: needsReview,
    };
    persistProgress(completedItems, updatedReviews);
  }

  function continuePreparation() {
    if (pendingEligibility.length > 0) {
      eligibilityRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
      return;
    }

    if (nextRound) {
      const nextKey = String(nextRound.id ?? `round-${nextRound.sourceIndex}`);
      setExpandedRoundId(nextKey);
      requestAnimationFrame(() =>
        roundRefs.current[nextKey]?.scrollIntoView({
          behavior: "smooth",
          block: "center",
        })
      );
      return;
    }

    if (roadmap.standaloneTopics.length > 0) {
      additionalPreparationRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
      return;
    }
    reviewRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  const hasUnassignedItems =
    roadmap.unassignedTopics.length > 0 ||
    roadmap.unassignedQuestions.length > 0;
  const firstIncompleteRoundKey = nextRound
    ? String(nextRound.id ?? `round-${nextRound.sourceIndex}`)
    : null;

  return (
    <section className="details-section interview-roadmap" aria-labelledby="interview-roadmap-title">
      <div className="details-section-heading interview-roadmap-heading">
        <div className="details-section-icon">
          <BookOpenCheck size={19} />
        </div>
        <div>
          <h2 id="interview-roadmap-title">Interview Preparation Roadmap</h2>
          <p>
            {companyName ? `${companyName}${jobRole ? ` · ${jobRole}` : ""}. ` : ""}
            Prepare for each recruitment round using collected topics and questions.
          </p>
        </div>
      </div>

      <div className="roadmap-progress">
        <div className="roadmap-progress-copy">
          <div className="roadmap-progress-title">
            <ListChecks size={17} />
            <strong>Your preparation progress</strong>
          </div>
          <span>
            {checklistCount
              ? `${completedCount} of ${checklistCount} preparation items completed`
              : "Progress will appear when preparation items are available"}
          </span>
        </div>
        <div
          className="roadmap-progress-track"
          role="progressbar"
          aria-label="Preparation progress"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={progress}
        >
          <span style={{ width: `${progress}%` }} />
        </div>
        <strong className="roadmap-progress-percent">{progress}%</strong>
      </div>

      {progressState.error && (
        <p className="roadmap-storage-error" role="status">
          {progressState.error}
        </p>
      )}

      <div className="journey-overview">
        <div className="journey-overview-copy">
          <div className="journey-kicker">
            <Sparkles size={14} />
            YOUR PLACEMENT JOURNEY
          </div>
          <div className="journey-title-row">
            <div>
              <h3>Prepare step by step</h3>
              <p>
                A focused path through the information collected for{" "}
                <strong>
                  {[companyName, jobRole].filter(Boolean).join(" · ") ||
                    "this placement drive"}
                </strong>
                .
              </p>
            </div>
            <button
              type="button"
              className="journey-continue-button"
              onClick={continuePreparation}
              disabled={!checklistCount}
            >
              {progress === 100 ? "Review your journey" : "Continue preparation"}
              <ArrowDown size={16} />
            </button>
          </div>
        </div>
        <div className="journey-stats-grid">
          <article className="journey-stat-card">
            <span className="journey-stat-icon indigo">
              <BriefcaseBusiness size={17} />
            </span>
            <div>
              <strong>{roadmap.rounds.length}</strong>
              <span>Recruitment rounds</span>
            </div>
          </article>
          <article className="journey-stat-card">
            <span className="journey-stat-icon blue">
              <BookOpenCheck size={17} />
            </span>
            <div>
              <strong>{topicItems.length}</strong>
              <span>
                Topics · {completedTopicCount} done · {remainingTopicCount} left
              </span>
            </div>
          </article>
          <article className="journey-stat-card">
            <span className="journey-stat-icon violet">
              <MessageSquareText size={17} />
            </span>
            <div>
              <strong>{questionItems.length}</strong>
              <span>Collected questions</span>
            </div>
          </article>
          <article className="journey-stat-card journey-total-progress">
            <span className="journey-stat-icon green">
              <Target size={17} />
            </span>
            <div>
              <strong>{progress}%</strong>
              <span>
                {completedCount} of {checklistCount} activities completed
              </span>
            </div>
          </article>
        </div>
      </div>

      {milestones.length > 0 && (
        <div className="roadmap-milestones" aria-label="Earned milestones">
          <span className="roadmap-milestones-label">
            <Award size={15} />
            Milestones
          </span>
          {milestones.map((milestone) => (
            <span className="roadmap-milestone" key={milestone.label}>
              <CheckCircle2 size={13} />
              {milestone.label}
            </span>
          ))}
        </div>
      )}

      {eligibilityItems.length > 0 && (
        <section
          className="roadmap-eligibility-step"
          ref={eligibilityRef}
          aria-label="Eligibility review"
        >
          <div className="roadmap-eligibility-heading">
            <span className="roadmap-step-number">
              <GraduationCap size={17} />
            </span>
            <div>
              <span className="roadmap-step-eyebrow">BEFORE YOU BEGIN</span>
              <h3>Review eligibility details</h3>
            </div>
          </div>
          <div className="roadmap-eligibility-list">
            {eligibilityItems.map(([key, value]) => {
              const itemKey = `eligibility:${driveId ?? "none"}:${key}`;
              return (
                <label
                  className={`roadmap-eligibility-item${completedItems[itemKey] ? " is-complete" : ""}`}
                  key={key}
                >
                  <input
                    type="checkbox"
                    checked={Boolean(completedItems[itemKey])}
                    onChange={(event) =>
                      updateCompletion(itemKey, event.target.checked)
                    }
                  />
                  <span className="roadmap-checkmark">
                    <CheckCircle2 size={16} />
                  </span>
                  <span>
                    <strong>{key.replaceAll("_", " ")}</strong>
                    <small>
                      {Array.isArray(value) ? value.join(", ") : String(value)}
                    </small>
                  </span>
                </label>
              );
            })}
          </div>
        </section>
      )}

      {roadmap.rounds.length > 0 ? (
        <div className="roadmap-timeline">
          {roadmap.rounds.map((round, index) => {
            const roundKey = String(round.id ?? `round-${round.sourceIndex}`);
            const roundChecklistKeys = [
              ...round.topics.map((topic) => topicChecklistKey(round, topic)),
              ...round.questions.map(questionChecklistKey),
            ];
            const roundChecklistCount = roundChecklistKeys.length;
            const roundCompletedCount = roundChecklistKeys.filter(
              (key) => completedItems[key]
            ).length;
            const roundProgress = roundChecklistCount
              ? Math.round((roundCompletedCount / roundChecklistCount) * 100)
              : 0;
            const roundTitle = round.round_type || `Round ${round.displayNumber}`;
            const needsRoundReview = roundChecklistKeys.some(
              (key) => reviewItems[key]
            );
            const roundStatus = needsRoundReview
              ? "Needs review"
              : roundChecklistCount > 0 && roundCompletedCount === roundChecklistCount
                ? "Completed"
                : roundCompletedCount > 0
                  ? "In progress"
                  : "Not started";
            const roundDifficultyOptions = Array.from(
              new Set(
                round.questions
                  .map((question) => question.difficulty)
                  .filter(Boolean)
              )
            );
            const selectedDifficulty = difficultyFilters[roundKey] || "all";
            const visibleRoundQuestions = round.questions.filter(
              (question) =>
                selectedDifficulty === "all" ||
                question.difficulty === selectedDifficulty
            );
            const questionGroups = round.topics
              .map((topic) => ({
                topic,
                questions: visibleRoundQuestions.filter(
                  (question) =>
                    normalizeId(question.topic_id) ===
                    normalizeId(topic.id ?? topic.topic_id)
                ),
              }))
              .filter((group) => group.questions.length > 0);
            const groupedQuestionKeys = new Set(
              questionGroups.flatMap((group) =>
                group.questions.map((question) => questionKey(question))
              )
            );
            const questionsWithoutTopic = round.questions.filter(
              (question) =>
                visibleRoundQuestions.includes(question) &&
                !groupedQuestionKeys.has(questionKey(question))
            );
            const renderQuestion = (question) => {
              const itemKey = questionChecklistKey(question);
              return (
                <RoadmapQuestion
                  key={question.id ?? questionKey(question)}
                  question={question}
                  topic={topicById.get(normalizeId(question.topic_id))}
                  itemKey={itemKey}
                  completed={Boolean(completedItems[itemKey])}
                  needsReview={Boolean(reviewItems[itemKey])}
                  onToggle={updateCompletion}
                  onReview={updateReview}
                />
              );
            };

            return (
              <details
                className={`roadmap-round ${roundStatus.toLowerCase().replace(/\s+/g, "-")}${firstIncompleteRoundKey === roundKey ? " is-current" : ""}`}
                key={roundKey}
                ref={(element) => {
                  roundRefs.current[roundKey] = element;
                }}
                open={
                  expandedRoundId === null
                    ? index === 0
                    : expandedRoundId === roundKey
                }
                onToggle={(event) => {
                  const isOpen = event.currentTarget.open;
                  setExpandedRoundId((current) =>
                    isOpen
                      ? roundKey
                      : current === roundKey
                        ? "__closed__"
                        : current
                  );
                }}
              >
                <summary className="roadmap-round-summary">
                  <span className="roadmap-step-number">{round.displayNumber}</span>
                  <span className="roadmap-round-title">
                    <strong>{roundTitle}</strong>
                    <span>{round.description || "Description not reported"}</span>
                    <span className="roadmap-round-status">
                      <i aria-hidden="true" />
                      {roundStatus}
                    </span>
                  </span>
                  <span className="roadmap-round-meta">
                    <span className="roadmap-round-count">
                      {round.topics.length} topic{round.topics.length === 1 ? "" : "s"}
                    </span>
                    {round.difficulty && (
                      <span
                        className={`roadmap-difficulty ${difficultyClass(round.difficulty)}`}
                      >
                        {round.difficulty}
                      </span>
                    )}
                    <span className="roadmap-round-count">
                      {round.questions.length} question
                      {round.questions.length === 1 ? "" : "s"}
                    </span>
                    <ChevronDown className="roadmap-chevron" size={18} />
                  </span>
                </summary>

                <div className="roadmap-round-content">
                  <div className="roadmap-round-progress">
                    <span>
                      {roundChecklistCount
                        ? `${roundCompletedCount}/${roundChecklistCount} items complete`
                        : "No preparation items collected for this round"}
                    </span>
                    <div className="roadmap-mini-progress">
                      <span style={{ width: `${roundProgress}%` }} />
                    </div>
                  </div>

                  {round.topics.length > 0 && (
                    <section className="roadmap-content-section">
                      <h3>
                        <Sparkles size={16} />
                        Learn · Topics to prepare
                      </h3>
                      <div className="roadmap-topic-list">
                        {round.topics.map((topic, topicIndex) => {
                          const itemKey = topicChecklistKey(round, topic);
                          const relatedQuestionCount = round.questions.filter(
                            (question) =>
                              normalizeId(question.topic_id) ===
                              normalizeId(topic.id ?? topic.topic_id)
                          ).length;

                          return (
                            <RoadmapTopic
                              key={`${topicContextKey(topic)}-${topicIndex}`}
                              topic={topic}
                              itemKey={itemKey}
                              completed={Boolean(completedItems[itemKey])}
                              needsReview={Boolean(reviewItems[itemKey])}
                              onToggle={updateCompletion}
                              onReview={updateReview}
                              relatedQuestionCount={relatedQuestionCount}
                            />
                          );
                        })}
                      </div>
                    </section>
                  )}
                  {round.topics.length === 0 && (
                    <p className="roadmap-no-checklist">
                      No topics collected for this round yet.
                    </p>
                  )}

                  <section className="roadmap-content-section">
                    <div className="roadmap-section-heading">
                      <h3>
                        <MessageSquareText size={16} />
                        Practise · Collected questions
                      </h3>
                      {roundDifficultyOptions.length > 0 && (
                        <label className="roadmap-difficulty-filter">
                          <span>Difficulty</span>
                          <select
                            value={selectedDifficulty}
                            onChange={(event) =>
                              setDifficultyFilters((current) => ({
                                ...current,
                                [roundKey]: event.target.value,
                              }))
                            }
                            aria-label={`Filter ${roundTitle} questions by difficulty`}
                          >
                            <option value="all">All levels</option>
                            {roundDifficultyOptions.map((difficulty) => (
                              <option key={difficulty} value={difficulty}>
                                {difficulty}
                              </option>
                            ))}
                          </select>
                        </label>
                      )}
                    </div>
                    {round.questions.length > 0 &&
                    visibleRoundQuestions.length === 0 ? (
                      <div className="roadmap-empty-questions">
                        <CircleHelp size={17} />
                        <p>No collected questions match this difficulty.</p>
                      </div>
                    ) : round.questions.length > 0 ? (
                      <>
                        {questionGroups.map((group) => (
                          <div
                            className="roadmap-question-group"
                            key={`topic-${normalizeId(group.topic.id ?? group.topic.topic_id)}`}
                          >
                            <h4>{group.topic.topic || group.topic.name}</h4>
                            <div className="roadmap-question-list">
                              {group.questions.map(renderQuestion)}
                            </div>
                          </div>
                        ))}
                        {questionsWithoutTopic.length > 0 && (
                          <div className="roadmap-question-group">
                            {questionGroups.length > 0 && (
                              <h4>Questions without a linked topic</h4>
                            )}
                            <div className="roadmap-question-list">
                              {questionsWithoutTopic.map(renderQuestion)}
                            </div>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="roadmap-empty-questions">
                        <CircleHelp size={17} />
                        <p>No interview questions collected for this round yet.</p>
                      </div>
                    )}
                  </section>

                  {roundChecklistCount === 0 && (
                    <p className="roadmap-no-checklist">
                      Preparation checklist items will appear when topics or questions are collected for this round.
                    </p>
                  )}
                </div>
              </details>
            );
          })}
        </div>
      ) : (
        <div className="roadmap-empty-rounds">
          <BookOpenCheck size={22} />
          <p>No recruitment rounds have been collected for this company yet.</p>
        </div>
      )}

      {roadmap.standaloneTechnicalTopics.length > 0 && (
        <section
          className="roadmap-technical-preparation"
          ref={
            roadmap.standaloneOtherTopics.length === 0
              ? additionalPreparationRef
              : null
          }
          aria-labelledby="roadmap-technical-title"
        >
          <div className="roadmap-unassigned-heading">
            <Sparkles size={18} />
            <div>
              <span className="roadmap-step-eyebrow">ADDITIONAL PREPARATION</span>
              <h3 id="roadmap-technical-title">Technical Preparation</h3>
              <p>
                These topics were reported separately and are not linked to a
                recruitment round.
              </p>
            </div>
          </div>
          <div className="roadmap-topic-list">
            {roadmap.standaloneTechnicalTopics.map((topic, index) => {
              const itemKey = topicChecklistKey(
                { id: "technical-preparation" },
                topic
              );
              return (
                <RoadmapTopic
                  key={`${topicContextKey(topic)}-${index}`}
                  topic={topic}
                  itemKey={itemKey}
                  completed={Boolean(completedItems[itemKey])}
                  needsReview={Boolean(reviewItems[itemKey])}
                  onToggle={updateCompletion}
                  onReview={updateReview}
                  relatedQuestionCount={roadmap.standaloneTechnicalQuestions.filter(
                    (question) =>
                      normalizeId(question.topic_id) ===
                        normalizeId(topic.id ?? topic.topic_id) &&
                      String(question.topic_category || topic.category || "")
                        .toLowerCase() === "technical"
                  ).length}
                />
              );
            })}
          </div>
          <section className="roadmap-content-section">
            <h4>Previously collected technical questions</h4>
            {roadmap.standaloneTechnicalQuestions.length > 0 ? (
              roadmap.standaloneTechnicalTopics.map((topic) => {
                const topicId = normalizeId(topic.id ?? topic.topic_id);
                const topicQuestions =
                  roadmap.standaloneTechnicalQuestions.filter(
                    (question) =>
                      normalizeId(question.topic_id) === topicId &&
                      String(question.topic_category || topic.category || "")
                        .toLowerCase() === "technical"
                  );
                if (topicQuestions.length === 0) return null;
                return (
                  <div
                    className="roadmap-question-group"
                    key={`technical-question-topic-${topicContextKey(topic)}`}
                  >
                    <h4>{topic.topic || topic.name}</h4>
                    <div className="roadmap-question-list">
                      {topicQuestions.map((question, index) => {
                        const itemKey = questionChecklistKey(question);
                        return (
                          <RoadmapQuestion
                            key={question.id ?? `${questionKey(question)}-${index}`}
                            question={question}
                            topic={topic}
                            itemKey={itemKey}
                            completed={Boolean(completedItems[itemKey])}
                            needsReview={Boolean(reviewItems[itemKey])}
                            onToggle={updateCompletion}
                            onReview={updateReview}
                          />
                        );
                      })}
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="roadmap-no-checklist">
                No interview questions collected for technical preparation yet.
              </p>
            )}
          </section>
        </section>
      )}

      {roadmap.standaloneOtherTopics.length > 0 && (
        <section
          className="roadmap-technical-preparation"
          ref={additionalPreparationRef}
          aria-labelledby="roadmap-standalone-title"
        >
          <div className="roadmap-unassigned-heading">
            <Sparkles size={18} />
            <div>
              <span className="roadmap-step-eyebrow">ADDITIONAL PREPARATION</span>
              <h3 id="roadmap-standalone-title">Other preparation topics</h3>
              <p>
                These collected topics were not explicitly associated with a
                recruitment round.
              </p>
            </div>
          </div>
          <div className="roadmap-topic-list">
            {roadmap.standaloneOtherTopics.map((topic, index) => {
              const itemKey = topicChecklistKey(
                { id: "standalone-preparation" },
                topic
              );
              return (
                <RoadmapTopic
                  key={`${topicContextKey(topic)}-${index}`}
                  topic={topic}
                  itemKey={itemKey}
                  completed={Boolean(completedItems[itemKey])}
                  needsReview={Boolean(reviewItems[itemKey])}
                  onToggle={updateCompletion}
                  onReview={updateReview}
                  relatedQuestionCount={roadmap.standaloneOtherQuestions.filter(
                    (question) =>
                      normalizeId(question.topic_id) ===
                        normalizeId(topic.id ?? topic.topic_id) &&
                      String(question.topic_category || topic.category || "")
                        .toLowerCase() ===
                        String(topic.category || "").toLowerCase()
                  ).length}
                />
              );
            })}
          </div>
          <section className="roadmap-content-section">
            <h4>Previously collected questions</h4>
            {roadmap.standaloneOtherQuestions.length > 0 ? (
              roadmap.standaloneOtherTopics.map((topic) => {
                const topicId = normalizeId(topic.id ?? topic.topic_id);
                const topicQuestions = roadmap.standaloneOtherQuestions.filter(
                  (question) =>
                    normalizeId(question.topic_id) === topicId &&
                    String(question.topic_category || topic.category || "")
                      .toLowerCase() ===
                      String(topic.category || "").toLowerCase()
                );
                if (topicQuestions.length === 0) return null;
                return (
                  <div
                    className="roadmap-question-group"
                    key={`standalone-question-topic-${topicContextKey(topic)}`}
                  >
                    <h4>{topic.topic || topic.name}</h4>
                    <div className="roadmap-question-list">
                      {topicQuestions.map((question, index) => {
                        const itemKey = questionChecklistKey(question);
                        return (
                          <RoadmapQuestion
                            key={question.id ?? `${questionKey(question)}-${index}`}
                            question={question}
                            topic={topic}
                            itemKey={itemKey}
                            completed={Boolean(completedItems[itemKey])}
                            needsReview={Boolean(reviewItems[itemKey])}
                            onToggle={updateCompletion}
                            onReview={updateReview}
                          />
                        );
                      })}
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="roadmap-no-checklist">
                No interview questions collected for these topics yet.
              </p>
            )}
          </section>
        </section>
      )}

      {hasUnassignedItems && (
        <section className="roadmap-unassigned" aria-labelledby="roadmap-unassigned-title">
          <div className="roadmap-unassigned-heading">
            <CircleHelp size={18} />
            <div>
              <h3 id="roadmap-unassigned-title">Unassigned Topics and Questions</h3>
              <p>These collected items do not have a usable round relationship.</p>
            </div>
          </div>

          {roadmap.unassignedTopics.length > 0 && (
            <div className="roadmap-unassigned-group">
              <h4>Topics not linked to a round</h4>
              <div className="roadmap-topic-list">
                {roadmap.unassignedTopics.map((topic, index) => {
                  const itemKey = topicChecklistKey({ id: "unassigned" }, topic);
                  return (
                    <RoadmapTopic
                      key={`${topicContextKey(topic)}-${index}`}
                      topic={topic}
                      itemKey={itemKey}
                      completed={Boolean(completedItems[itemKey])}
                      needsReview={Boolean(reviewItems[itemKey])}
                      onToggle={updateCompletion}
                      onReview={updateReview}
                    />
                  );
                })}
              </div>
            </div>
          )}

          {roadmap.unassignedQuestions.length > 0 && (
            <div className="roadmap-unassigned-group">
              <h4>Questions not linked to a round</h4>
              <div className="roadmap-question-list">
                {roadmap.unassignedQuestions.map((question, index) => {
                  const itemKey = questionChecklistKey(question);
                  return (
                    <RoadmapQuestion
                      key={
                        question.id ??
                        `unassigned-${questionKey(question)}-${index}`
                      }
                      question={question}
                      topic={topicById.get(normalizeId(question.topic_id))}
                      itemKey={itemKey}
                      completed={Boolean(completedItems[itemKey])}
                      needsReview={Boolean(reviewItems[itemKey])}
                      onToggle={updateCompletion}
                      onReview={updateReview}
                    />
                  );
                })}
              </div>
            </div>
          )}
        </section>
      )}

      {checklistCount > 0 && (
        <section
          className="roadmap-review-center"
          ref={reviewRef}
          aria-labelledby="roadmap-review-title"
        >
          <div className="roadmap-review-center-heading">
            <div className="roadmap-review-center-icon">
              <RotateCcw size={18} />
            </div>
            <div>
              <h3 id="roadmap-review-title">Review and revise</h3>
              <p>
                {reviewCount
                  ? `${reviewCount} item${reviewCount === 1 ? "" : "s"} flagged for another look`
                  : "Flag topics or questions whenever you want to revisit them."}
              </p>
            </div>
          </div>

          {reviewCount > 0 ? (
            <div className="roadmap-review-list">
              {uniqueChecklistItems
                .filter((item) => reviewItems[item.key])
                .map((item) => (
                  <article className="roadmap-review-item" key={item.key}>
                    <span className="roadmap-review-item-type">{item.type}</span>
                    <div>
                      <strong>{item.label}</strong>
                      <small>{item.section}</small>
                      <span className="roadmap-review-progress">
                        {completedItems[item.key] ? "Completed · revisit" : "Still to complete"}
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => updateReview(item.key, false)}
                      aria-label={`Remove ${item.label} from review list`}
                    >
                      Remove
                    </button>
                  </article>
                ))}
            </div>
          ) : (
            <p className="roadmap-review-empty">
              Nothing is waiting for revision. Use the review icon beside any
              topic or question to add it here.
            </p>
          )}

          <details className="roadmap-completed-details">
            <summary>
              <CheckCircle2 size={15} />
              Completed activities ({completedCount})
              <ChevronDown size={16} />
            </summary>
            {completedCount > 0 ? (
              <div className="roadmap-review-list">
                {uniqueChecklistItems
                  .filter((item) => completedItems[item.key])
                  .map((item) => (
                    <article className="roadmap-review-item is-complete" key={item.key}>
                      <span className="roadmap-review-item-type">{item.type}</span>
                      <div>
                        <strong>{item.label}</strong>
                        <small>{item.section}</small>
                      </div>
                      <button
                        type="button"
                        onClick={() => updateCompletion(item.key, false)}
                        aria-label={`Mark ${item.label} as not completed`}
                      >
                        Undo
                      </button>
                    </article>
                  ))}
              </div>
            ) : (
              <p className="roadmap-review-empty">
                Completed activities will appear here.
              </p>
            )}
          </details>
        </section>
      )}

      {checklistCount > 0 && progress === 100 && (
        <div className="roadmap-ready-state" role="status">
          <span>
            <Trophy size={21} />
          </span>
          <div>
            <strong>Preparation completed</strong>
            <p>You’ve completed every activity in this collected roadmap.</p>
          </div>
          <span className="roadmap-ready-percent">100%</span>
        </div>
      )}

      <p className="roadmap-data-note">
        Question and topic associations come from collected feedback. This roadmap does not add company-specific facts.
      </p>
    </section>
  );
}

export default InterviewPreparationRoadmap;

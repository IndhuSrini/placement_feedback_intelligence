import { useEffect, useRef, useState } from "react";
import {
  CircleCheck,
  Send,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import "./PlacementAssistant.css";

const API = "/api";
const NOT_FOUND = "I couldn't find that information in the current placement database.";
const COMPANY_NOT_FOUND = "I couldn't find that company in the current placement database.";
const SUGGESTIONS = [
  { label: "What should I prepare?", query: "What should I prepare?" },
  { label: "Interview questions", query: "What interview questions are common?" },
  { label: "Company eligibility", query: "What is the eligibility?" },
  { label: "Frequent topics", query: "Which technical topics are common?" },
  { label: "Recruitment rounds", query: "What are the recruitment rounds?" },
  { label: "How many companies?", query: "How many companies are available?" },
];

const COMPANY_QUERY_STOP_WORDS = new Set((
  "a about all an and any are as at available be can could do does did " +
  "for from give has have how i in information is it me my of on or " +
  "please show tell than that the their them there they this to we what " +
  "which who would you your company companies drive drives placement " +
  "question questions ques interview asked ask come practice practise " +
  "topic topics technical area areas subject subjects eligibility eligible " +
  "cgpa backlog backlogs requirement requirements apply prepare preparation " +
  "study frequent frequently common most popular occur occurrence rounds " +
  "round recruitment hiring selection process stages stage details about " +
  "total number count many stored recorded available analytics statistics recruitment " +
  "who should its their latest process candidates candidates"
).split(/\s+/));

const COUNT_SIGNAL = /\b(?:how many|total|number of|count)\b|\b(?:company|drive|question|topic) count\b/;
const COMPANY_LIST_SIGNAL = /\b(?:companies available|available companies|list companies|what companies|which companies|show (?:all )?companies|company directory)\b/;
const ELIGIBILITY_SIGNAL = /\b(?:eligibility|eligible|cgpa|backlogs?|requirements?|apply|qualify|qualification)\b/;
const ROUND_SIGNAL = /\b(?:rounds?|recruitment process|recruitment work|selection process|hiring process|interview process|stages?)\b/;
const QUESTION_SIGNAL = /\b(?:questions?|ques|practice|practise|what do they ask|what did they ask|what comes|what is asked|what are asked)\b/;
const TOPIC_SIGNAL = /\b(?:topics?|technical areas?|areas?|subjects?|technical preparation)\b/;
const PREPARATION_SIGNAL = /\b(?:prepare|preparation|study|revise)\b/;
const TOPIC_PREPARATION_SIGNAL = /\b(?:study|revise)\b|\bprepare in\b/;
const COMPANY_INFO_SIGNAL = /\b(?:tell me about|do we have|do you have|available|details?|information about|company information|what is|show)\b/;
const COMPANY_REFERENCE_SIGNAL = /\b(?:it|its|they|them|their|that company|this company|what about|and its|and their)\b/;

function normalizeQuery(value) {
  return String(value || "")
    .toLowerCase()
    .trim()
    .replace(/what['’]s\b/g, "what is")
    .replace(/what['’]re\b/g, "what are")
    .replace(/who['’]s\b/g, "who is")
    .replace(/don['’]t\b/g, "do not")
    .replace(/\bques\b/g, "questions")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function getCompanyQueryTokens(normalizedQuery) {
  return normalizedQuery
    .split(" ")
    .filter((token) => token.length >= 4 && !COMPANY_QUERY_STOP_WORDS.has(token));
}

function editDistance(first, second) {
  const previousPrevious = [];
  let previous = Array.from({ length: second.length + 1 }, (_, index) => index);

  for (let firstIndex = 1; firstIndex <= first.length; firstIndex += 1) {
    const current = [firstIndex];
    for (let secondIndex = 1; secondIndex <= second.length; secondIndex += 1) {
      const substitutionCost = first[firstIndex - 1] === second[secondIndex - 1] ? 0 : 1;
      current[secondIndex] = Math.min(
        current[secondIndex - 1] + 1,
        previous[secondIndex] + 1,
        previous[secondIndex - 1] + substitutionCost,
      );

      if (
        firstIndex > 1 &&
        secondIndex > 1 &&
        first[firstIndex - 1] === second[secondIndex - 2] &&
        first[firstIndex - 2] === second[secondIndex - 1]
      ) {
        current[secondIndex] = Math.min(
          current[secondIndex],
          (previousPrevious[secondIndex - 2] ?? Number.MAX_SAFE_INTEGER) + 1,
        );
      }
    }
    previousPrevious.splice(0, previousPrevious.length, ...previous);
    previous = current;
  }

  return previous[second.length];
}

function resolveCompany(message, companies) {
  const normalizedQuery = normalizeQuery(message);
  const candidates = [...companies].filter((company) => company?.name);
  const exactMatches = candidates
    .filter((company) => {
      const normalizedName = normalizeQuery(company.name);
      return normalizedName && ` ${normalizedQuery} `.includes(` ${normalizedName} `);
    })
    .sort((first, second) => second.name.length - first.name.length);

  if (exactMatches.length) {
    return { company: exactMatches[0], confidence: "exact", queryTokens: [] };
  }

  const queryTokens = getCompanyQueryTokens(normalizedQuery);
  const fuzzyCandidates = [];
  for (const company of candidates) {
    const companyTokens = normalizeQuery(company.name).split(" ").filter((token) => token.length >= 4);
    let bestMatch = null;
    for (const queryToken of queryTokens) {
      for (const companyToken of companyTokens) {
        const maxLength = Math.max(queryToken.length, companyToken.length);
        if (Math.abs(queryToken.length - companyToken.length) > 2) continue;
        const distance = editDistance(queryToken, companyToken);
        const similarity = 1 - distance / maxLength;
        const maxAcceptedDistance = maxLength >= 7 ? 2 : 1;
        if (!bestMatch || similarity > bestMatch.similarity) {
          bestMatch = { similarity, distance, maxAcceptedDistance };
        }
      }
    }
    if (bestMatch) fuzzyCandidates.push({ company, ...bestMatch });
  }

  fuzzyCandidates.sort((first, second) => second.similarity - first.similarity);
  const best = fuzzyCandidates[0];
  if (!best) return { company: null, confidence: "none", queryTokens };

  const next = fuzzyCandidates[1];
  if (
    best.similarity >= 0.70 &&
    best.distance <= best.maxAcceptedDistance &&
    (!next || best.similarity - next.similarity >= 0.06)
  ) {
    return { company: best.company, confidence: "fuzzy", queryTokens };
  }
  if (best.similarity >= 0.56) {
    return { company: null, confidence: "ambiguous", suggestion: best.company, queryTokens };
  }
  return { company: null, confidence: "none", queryTokens };
}

function detectIntent(normalizedQuery, hasCompany = false) {
  const hasCountSignal = COUNT_SIGNAL.test(normalizedQuery);
  if (!hasCompany && hasCountSignal) {
    if (/\b(?:companies|company)\b/.test(normalizedQuery)) return "total_companies";
    if (/\b(?:drives?|placement)\b/.test(normalizedQuery)) return "total_drives";
    if (/\b(?:questions?|interview questions?)\b/.test(normalizedQuery)) return "total_questions";
    if (/\b(?:topics?|technical topics?)\b/.test(normalizedQuery)) return "total_topics";
  }
  if (COMPANY_LIST_SIGNAL.test(normalizedQuery)) return "company_list";
  if (ELIGIBILITY_SIGNAL.test(normalizedQuery)) return "company_eligibility";
  if (ROUND_SIGNAL.test(normalizedQuery)) return "recruitment_rounds";

  const hasQuestionSignal = QUESTION_SIGNAL.test(normalizedQuery);
  const hasTopicSignal = TOPIC_SIGNAL.test(normalizedQuery);
  if (hasQuestionSignal && hasTopicSignal) return "combined_preparation";
  if (!hasQuestionSignal && hasTopicSignal && /\b(?:asked|ask)\b/.test(normalizedQuery)) return "frequent_topics";
  if (hasQuestionSignal) return "frequent_questions";
  if (hasTopicSignal) return "frequent_topics";
  if (TOPIC_PREPARATION_SIGNAL.test(normalizedQuery)) return "frequent_topics";
  if (PREPARATION_SIGNAL.test(normalizedQuery)) return "preparation";
  if (/\binterview\b/.test(normalizedQuery)) return "ambiguous_interview";
  if (/\b(?:placement analytics|placement statistics|analytics summary|overall statistics|overall analytics)\b/.test(normalizedQuery)) {
    return "general_analytics";
  }
  if (COMPANY_INFO_SIGNAL.test(normalizedQuery) || hasCompany) return "company_information";
  return "unknown";
}

function asksAboutPreviousCompany(normalizedQuery) {
  return COMPANY_REFERENCE_SIGNAL.test(normalizedQuery);
}

async function getJson(path) {
  try {
    const response = await fetch(`${API}${path}`);
    if (!response.ok) throw new Error("Request failed");
    return await response.json();
  } catch {
    throw new Error("service_unavailable");
  }
}

function hasValue(value) {
  return value !== undefined && value !== null && value !== "" && value !== "None" && value !== "null";
}

function formatInline(text) {
  return text.split(/(\*\*.*?\*\*)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

function FormattedAnswer({ text }) {
  return (
    <div className="placement-assistant-answer">
      {text.split("\n").map((line, index) => {
        const numbered = line.match(/^(\d+)[.)]\s+(.*)$/);
        const bulleted = line.match(/^[•-]\s+(.*)$/);

        if (numbered) {
          return (
            <div className="placement-assistant-list-row" key={index}>
              <span className="placement-assistant-list-number">{numbered[1]}.</span>
              <span>{formatInline(numbered[2])}</span>
            </div>
          );
        }
        if (bulleted) {
          return (
            <div className="placement-assistant-list-row" key={index}>
              <span className="placement-assistant-list-dot">•</span>
              <span>{formatInline(bulleted[1])}</span>
            </div>
          );
        }
        if (!line.trim()) return <div className="placement-assistant-answer-spacer" key={index} />;
        return <p key={index}>{formatInline(line)}</p>;
      })}
    </div>
  );
}

function formatCompanyEligibility(company, details) {
  const eligibility = details.eligibility || {};
  const lines = [`**${company.name} Eligibility**`, "Based on the available company placement data:"];

  if (hasValue(eligibility.minimum_cgpa)) {
    lines.push(`• Minimum CGPA: **${eligibility.minimum_cgpa}**`);
  }
  if (hasValue(eligibility.maximum_backlogs)) {
    const backlogText = Number(eligibility.maximum_backlogs) === 0
      ? "No active backlogs allowed"
      : `Maximum ${eligibility.maximum_backlogs} backlog(s)`;
    lines.push(`• Backlogs: **${backlogText}**`);
  }
  if (hasValue(eligibility.branch_eligibility)) {
    lines.push(`• Eligible branches: **${eligibility.branch_eligibility}**`);
  }
  if (hasValue(eligibility.other_criteria)) {
    lines.push(`• Other criteria: **${eligibility.other_criteria}**`);
  }

  return lines.length > 2 ? lines.join("\n") : NOT_FOUND;
}

function formatTopics(companyName, rawTopics) {
  const topics = Array.isArray(rawTopics)
    ? rawTopics.filter((topic) => topic && hasValue(topic.topic || topic.name))
    : [];
  if (!topics.length) return NOT_FOUND;

  const lines = [`**Frequent ${companyName} Topics**`, "Based on the available company placement data:"];
  topics.slice(0, 8).forEach((topic, index) => {
    const name = topic.topic || topic.name;
    const count = hasValue(topic.occurrence_count) ? ` — ${topic.occurrence_count} occurrence(s)` : "";
    lines.push(`${index + 1}. ${name}${count}`);
  });
  return lines.join("\n");
}

function formatQuestions(companyName, rawQuestions) {
  const seen = new Set();
  const questions = (Array.isArray(rawQuestions) ? rawQuestions : []).filter((question) => {
    const text = String(question?.question || question?.question_text || "").trim();
    const key = text.toLowerCase().replace(/[^a-z0-9]/g, "");
    if (text.length < 8 || !key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  if (!questions.length) return NOT_FOUND;

  const lines = [`**Frequently Asked ${companyName} Questions**`, "Based on the available company placement data:"];
  questions.slice(0, 8).forEach((question, index) => {
    const text = String(question.question || question.question_text).trim();
    lines.push(`${index + 1}. ${text}`);
    const details = [];
    if (hasValue(question.occurrence_count)) details.push(`Frequency: ${question.occurrence_count}`);
    if (hasValue(question.difficulty)) details.push(`Difficulty: ${question.difficulty}`);
    if (hasValue(question.category)) details.push(`Category: ${question.category}`);
    if (details.length) lines.push(`   ${details.join(" · ")}`);
  });
  return lines.join("\n");
}

function formatRounds(companyName, rawRounds) {
  const rounds = (Array.isArray(rawRounds) ? rawRounds : [])
    .filter((round) => hasValue(round?.round_type || round?.description))
    .sort((first, second) => {
      const firstNumber = hasValue(first.round_number) ? Number(first.round_number) : Number.NaN;
      const secondNumber = hasValue(second.round_number) ? Number(second.round_number) : Number.NaN;
      if (!Number.isFinite(firstNumber)) return Number.isFinite(secondNumber) ? 1 : 0;
      if (!Number.isFinite(secondNumber)) return -1;
      return firstNumber - secondNumber;
    });
  if (!rounds.length) return NOT_FOUND;

  const lines = [`**${companyName} Recruitment Process**`, "Based on the available company placement data:"];
  rounds.forEach((round) => {
    const label = round.round_type || round.description;
    const number = hasValue(round.round_number) ? Number(round.round_number) : Number.NaN;
    const prefix = Number.isFinite(number) ? `${number}.` : "•";
    lines.push(`${prefix} **${label}**`);
    if (hasValue(round.description) && round.description !== label) {
      lines.push(`   ${round.description}`);
    }
    if (hasValue(round.difficulty)) lines.push(`   Difficulty: ${round.difficulty}`);
  });
  return lines.join("\n");
}

function formatGlobalTopics(rawTopics) {
  const topics = Array.isArray(rawTopics) ? rawTopics.filter((topic) => hasValue(topic?.topic)) : [];
  if (!topics.length) return NOT_FOUND;
  const lines = ["**Most Frequent Placement Topics**"];
  topics.slice(0, 8).forEach((topic, index) => {
    const count = hasValue(topic.occurrence_count) ? ` — ${topic.occurrence_count} occurrence(s)` : "";
    const category = hasValue(topic.category) ? ` (${topic.category})` : "";
    lines.push(`${index + 1}. ${topic.topic}${category}${count}`);
  });
  return lines.join("\n");
}

function formatGlobalQuestions(rawQuestions) {
  const questions = (Array.isArray(rawQuestions) ? rawQuestions : [])
    .filter((question) => String(question?.question || "").trim().length >= 8);
  if (!questions.length) return NOT_FOUND;
  const lines = ["**Frequently Asked Placement Questions**"];
  questions.slice(0, 8).forEach((question, index) => {
    lines.push(`${index + 1}. ${question.question.trim()}`);
    const details = [];
    if (hasValue(question.occurrence_count)) details.push(`Frequency: ${question.occurrence_count}`);
    if (hasValue(question.difficulty)) details.push(`Difficulty: ${question.difficulty}`);
    if (details.length) lines.push(`   ${details.join(" · ")}`);
  });
  return lines.join("\n");
}

function formatCompanyInformation(company, details) {
  const lines = [`**${company.name}**`, "Based on the available company placement data:"];
  if (hasValue(company.industry)) lines.push(`• Industry: **${company.industry}**`);
  if (hasValue(company.website)) lines.push(`• Website: **${company.website}**`);
  if (hasValue(details.placement_drives)) lines.push(`• Placement drives recorded: **${details.placement_drives}**`);
  if (hasValue(details.job_role)) lines.push(`• Latest reported role: **${details.job_role}**`);
  if (hasValue(details.recruitment_date)) lines.push(`• Latest reported recruitment date: **${details.recruitment_date}**`);
  if (hasValue(details.year)) lines.push(`• Recruitment year: **${details.year}**`);
  lines.push("Company details reflect the latest drive where a company has multiple drives.");
  return lines.join("\n");
}

function formatOverview(overview) {
  const fields = [
    ["Companies", overview.total_companies],
    ["Placement drives", overview.total_placement_drives],
    ["Questions stored", overview.total_questions],
    ["Topics", overview.total_topics],
    ["Recruitment rounds", overview.total_recruitment_rounds],
  ].filter(([, value]) => hasValue(value));
  if (!fields.length) return NOT_FOUND;
  return ["**Placement Intelligence Overview**", ...fields.map(([label, value]) => `• ${label}: **${value}**`)].join("\n");
}

function formatMetric(overview, intent) {
  const metrics = {
    total_companies: ["companies", overview.total_companies],
    total_drives: ["placement drives", overview.total_placement_drives],
    total_questions: ["questions", overview.total_questions],
    total_topics: ["technical topics", overview.total_topics],
  };
  const [label, value] = metrics[intent] || [];
  if (!hasValue(value)) return NOT_FOUND;
  const verb = Number(value) === 1 ? "is" : "are";
  const suffix = intent === "total_questions" ? "stored" : "recorded";
  return `There ${verb} **${value} ${label}** ${suffix} in the placement database.`;
}

export default function PlacementAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [lastCompany, setLastCompany] = useState(null);
  const launcherRef = useRef(null);
  const inputRef = useRef(null);
  const endOfMessagesRef = useRef(null);
  const companiesPromiseRef = useRef(null);
  const wasOpenRef = useRef(false);

  useEffect(() => {
    if (isOpen) {
      wasOpenRef.current = true;
      inputRef.current?.focus();
    } else if (wasOpenRef.current) {
      wasOpenRef.current = false;
      launcherRef.current?.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ block: "end" });
  }, [messages, isLoading]);

  useEffect(() => {
    if (!isOpen) return undefined;
    function handleKeyDown(event) {
      if (event.key === "Escape") setIsOpen(false);
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  async function getCompanies() {
    if (!companiesPromiseRef.current) {
      companiesPromiseRef.current = getJson("/companies/")
        .then((data) => (Array.isArray(data) ? data : []))
        .catch((error) => {
          companiesPromiseRef.current = null;
          throw error;
        });
    }
    return companiesPromiseRef.current;
  }

  async function loadCompanyDetails(company) {
    const details = await getJson(`/analytics/company/${company.id}`);
    return details.error ? null : details;
  }

  async function answerQuery(message) {
    const normalizedQuery = normalizeQuery(message);
    const preliminaryIntent = detectIntent(normalizedQuery);
    const isGlobalCount = ["total_companies", "total_drives", "total_questions", "total_topics"].includes(preliminaryIntent)
      && getCompanyQueryTokens(normalizedQuery).length === 0;

    if (isGlobalCount) {
      return formatMetric(await getJson("/analytics/overview"), preliminaryIntent);
    }
    if (preliminaryIntent === "general_analytics") {
      return formatOverview(await getJson("/analytics/overview"));
    }

    const companies = await getCompanies();
    if (preliminaryIntent === "company_list") {
      if (!companies.length) return NOT_FOUND;
      const lines = ["**Companies in the placement database**", ...companies.slice(0, 15).map((company, index) => `${index + 1}. ${company.name}`)];
      if (companies.length > 15) lines.push(`Showing 15 of ${companies.length} companies.`);
      return lines.join("\n");
    }

    const resolution = resolveCompany(message, companies);
    if (resolution.confidence === "ambiguous") {
      return `I couldn't confidently match that company. Did you mean **${resolution.suggestion.name}**?`;
    }

    const usesContext = !resolution.company && lastCompany && asksAboutPreviousCompany(normalizedQuery);
    const company = resolution.company || (usesContext ? lastCompany : null);
    if (resolution.company) setLastCompany(resolution.company);

    const intent = detectIntent(normalizedQuery, Boolean(company));
    if (intent === "unknown") {
      return "I can help with:\n• Company eligibility\n• Frequent interview questions\n• Frequent technical topics\n• Recruitment rounds\n• Company information\n• Placement statistics\n\nTry asking: 'LTIMindtree questions' or 'What is the eligibility for Infosys?'";
    }

    if (intent === "ambiguous_interview") {
      if (company) {
        return `Would you like the frequent topics, interview questions, or recruitment rounds for ${company.name}?`;
      }
      return "Would you like frequent topics, interview questions, or recruitment rounds for a company?";
    }

    if (intent === "preparation" || intent === "combined_preparation") {
      if (!company) {
        return "Which company should I look up? I can combine its frequent topics, interview questions, and recruitment rounds.";
      }
      const details = await loadCompanyDetails(company);
      if (!details) return COMPANY_NOT_FOUND;
      const sections = [
        formatTopics(company.name, details.topics),
        formatQuestions(company.name, details.frequent_questions),
        formatRounds(company.name, details.rounds),
      ].filter((section) => section !== NOT_FOUND);
      return sections.length ? sections.join("\n\n") : NOT_FOUND;
    }

    if (intent === "frequent_topics" || intent === "frequent_questions") {
      if (!company && resolution.queryTokens.length) return COMPANY_NOT_FOUND;
      if (!company && usesContext) return COMPANY_NOT_FOUND;
      if (company) {
        const details = await loadCompanyDetails(company);
        if (!details) return COMPANY_NOT_FOUND;
        return intent === "frequent_topics"
          ? formatTopics(company.name, details.topics)
          : formatQuestions(company.name, details.frequent_questions);
      }
      return intent === "frequent_topics"
        ? formatGlobalTopics(await getJson("/analytics/frequent-topics"))
        : formatGlobalQuestions(await getJson("/analytics/frequent-questions"));
    }

    if (intent === "company_eligibility" || intent === "recruitment_rounds" || intent === "company_information") {
      if (!company) {
        if (resolution.queryTokens.length) return COMPANY_NOT_FOUND;
        return "Which company would you like information about?";
      }
      const details = await loadCompanyDetails(company);
      if (!details) return COMPANY_NOT_FOUND;
      if (intent === "company_eligibility") return formatCompanyEligibility(company, details);
      if (intent === "recruitment_rounds") return formatRounds(company.name, details.rounds);
      return formatCompanyInformation(company, details);
    }

    return NOT_FOUND;
  }

  async function sendMessage(message = draft) {
    const text = message.trim();
    if (!text || isLoading) return;

    setMessages((current) => [...current, { role: "user", text }]);
    setDraft("");
    setIsLoading(true);

    try {
      const answer = await answerQuery(text);
      setMessages((current) => [...current, { role: "assistant", text: answer }]);
    } catch {
      setMessages((current) => [...current, {
        role: "assistant",
        text: "I couldn't connect to the placement intelligence service. Please make sure the backend is running.",
      }]);
    } finally {
      setIsLoading(false);
    }
  }

  function handleInputKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  return (
    <>
      {!isOpen && (
        <button
          ref={launcherRef}
          type="button"
          className="placement-assistant-launcher"
          aria-label="Placement Assistant"
          title="Placement Assistant"
          onClick={() => setIsOpen(true)}
        >
          <Sparkles size={21} aria-hidden="true" />
        </button>
      )}

      {isOpen && (
        <>
          <button
            type="button"
            className="placement-assistant-backdrop"
            aria-label="Close Placement Assistant"
            onClick={() => setIsOpen(false)}
          />
          <aside
            className="placement-assistant-panel"
            role="dialog"
            aria-modal="true"
            aria-labelledby="placement-assistant-title"
          >
            <header className="placement-assistant-header">
              <div className="placement-assistant-header-icon">
                <Sparkles size={18} aria-hidden="true" />
              </div>
              <div className="placement-assistant-header-copy">
                <h2 id="placement-assistant-title">Placement Assistant</h2>
                <p>Ask about placement intelligence</p>
              </div>
              <button
                type="button"
                className="placement-assistant-icon-button"
                aria-label="Close Placement Assistant"
                title="Close assistant"
                onClick={() => setIsOpen(false)}
              >
                <X size={18} aria-hidden="true" />
              </button>
            </header>

            <div className="placement-assistant-conversation" aria-live="polite" aria-relevant="additions text">
              {messages.length === 0 ? (
                <div className="placement-assistant-welcome">
                  <div className="placement-assistant-welcome-mark">
                    <Sparkles size={18} aria-hidden="true" />
                  </div>
                  <p>Hi! I can help you explore placement intelligence.</p>
                  <div className="placement-assistant-suggestions">
                    {SUGGESTIONS.map((suggestion) => (
                      <button
                        type="button"
                        key={suggestion.label}
                        disabled={isLoading}
                        onClick={() => sendMessage(suggestion.query)}
                      >
                        {suggestion.label}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <>
                  <div className="placement-assistant-chat-toolbar">
                    <span>Conversation</span>
                    <button type="button" onClick={() => setMessages([])} disabled={isLoading}>
                      <Trash2 size={13} aria-hidden="true" />
                      Clear chat
                    </button>
                  </div>
                  {messages.map((message, index) => (
                    <div className={`placement-assistant-message ${message.role}`} key={`${message.role}-${index}`}>
                      {message.role === "assistant" && (
                        <span className="placement-assistant-message-icon">
                          <Sparkles size={13} aria-hidden="true" />
                        </span>
                      )}
                      <div className="placement-assistant-bubble">
                        {message.role === "assistant"
                          ? <FormattedAnswer text={message.text} />
                          : message.text}
                      </div>
                    </div>
                  ))}
                </>
              )}
              {isLoading && (
                <div className="placement-assistant-message assistant">
                  <span className="placement-assistant-message-icon">
                    <Sparkles size={13} aria-hidden="true" />
                  </span>
                  <div className="placement-assistant-bubble placement-assistant-loading" role="status">
                    <span>Analyzing placement data...</span>
                    <span className="placement-assistant-dots" aria-hidden="true"><i /><i /><i /></span>
                  </div>
                </div>
              )}
              <div ref={endOfMessagesRef} />
            </div>

            <form
              className="placement-assistant-composer"
              onSubmit={(event) => {
                event.preventDefault();
                sendMessage();
              }}
            >
              <textarea
                ref={inputRef}
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={handleInputKeyDown}
                placeholder="Ask about placement data..."
                aria-label="Ask about placement data"
                rows={1}
                disabled={isLoading}
              />
              <button
                type="submit"
                aria-label="Send message"
                title="Send message"
                disabled={isLoading || !draft.trim()}
              >
                <Send size={17} aria-hidden="true" />
              </button>
              <span className="placement-assistant-composer-hint">Enter to send · Shift+Enter for a new line</span>
            </form>

            <div className="placement-assistant-data-note">
              <CircleCheck size={13} aria-hidden="true" />
              <span>Answers use placement data currently stored in the system.</span>
            </div>
          </aside>
        </>
      )}
    </>
  );
}
import { useEffect, useMemo, useState, useCallback } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import {
  ArrowLeft,
  Building2,
  BriefcaseBusiness,
  CalendarDays,
  CheckCircle2,
  CircleAlert,
  Code2,
  ExternalLink,
  FileDown,
  GraduationCap,
  Layers3,
  Loader2,
  MessageSquareText,
  RefreshCw,
  Target,
  Users,
  Brain,
  Sparkles,
  Trophy,
  HelpCircle,
  ShieldCheck,
  AlertCircle,
  BarChart2,
} from "lucide-react";

import { getCompanyWebsite } from "../utils/companyWebsites";
import { generateCompanyPdfReport } from "../utils/pdfGenerator";
import InterviewPreparationRoadmap from "../components/InterviewPreparationRoadmap";

const API = "/api";

function formatDate(value) {
  if (!value) return "Not reported";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function displayValue(value, fallback = "Not reported") {
  if (
    value === undefined ||
    value === null ||
    value === "" ||
    value === "null" ||
    value === "None"
  ) {
    return fallback;
  }
  return value;
}

function cleanQuestionText(text) {
  if (!text) return "";
  return String(text)
    .replace(/\*\*/g, "")
    .replace(/__/g, "")
    .replace(/^["']|["']$/g, "")
    .replace(/^\d+[.)]\s*/, "")
    .trim();
}

/*
 * Use real recruitment rounds returned by the backend without inventing stages.
 * Deduplicates exact semantic repeats and sorts by round_number if present.
 */
function processRounds(rawRounds) {
  if (!Array.isArray(rawRounds) || rawRounds.length === 0) {
    return [];
  }

  const seen = new Set();
  const deduped = [];

  for (const round of rawRounds) {
    const rName = String(round.displayName || round.round_name || round.round_type || round.name || "").trim();
    const rDesc = String(round.description || "").trim();
    const normName = rName.toLowerCase();
    const normDesc = rDesc.toLowerCase();

    // Deduplicate exact semantic duplicates (e.g. name="HR", desc="HR" or "HR Round")
    const key =
      normDesc === normName ||
      normDesc === `${normName} round` ||
      normDesc === `${normName} interview` ||
      !rDesc
        ? normName
        : `${normName}:${normDesc}`;

    if (!seen.has(key)) {
      seen.add(key);
      deduped.push({
        ...round,
        displayName: rName || "Assessment Stage",
      });
    }
  }

  return deduped.sort((a, b) => {
    const numA = Number(a.round_number) || 999;
    const numB = Number(b.round_number) || 999;
    return numA - numB;
  });
}

function DifficultyTooltip({ active, payload }) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const item = payload[0].payload;

  return (
    <div className="analytics-tooltip">
      <p>{item.name} Difficulty</p>
      <strong>{item.count} question{item.count === 1 ? "" : "s"}</strong>
    </div>
  );
}

function CompanyDetails() {
  const { companyId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedDriveId = searchParams.get("drive_id") || "";

  const [company, setCompany] = useState(null);
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  /*
   * Load company analytics and company information.
   */
  const loadCompanyDetails = useCallback(
    async (isRefresh = false) => {
      try {
        if (isRefresh) {
          setRefreshing(true);
        } else {
          setLoading(true);
        }
        setError("");

        const detailsResponse = await fetch(
          `${API}/analytics/company/${companyId}${
            selectedDriveId
              ? `?drive_id=${encodeURIComponent(selectedDriveId)}`
              : ""
          }`
        );

        if (!detailsResponse.ok) {
          throw new Error(
            `Failed to load company intelligence: ${detailsResponse.status}`
          );
        }

        const detailsData = await detailsResponse.json();
        setDetails(detailsData);

        try {
          const companiesResponse = await fetch(`${API}/companies/`);
          if (companiesResponse.ok) {
            const companiesData = await companiesResponse.json();
            const selectedCompany = Array.isArray(companiesData)
              ? companiesData.find(
                  (item) => String(item.id) === String(companyId)
                )
              : null;
            setCompany(selectedCompany);
          }
        } catch (companyError) {
          console.warn("Could not load additional company metadata:", companyError);
        }
      } catch (err) {
        console.error("Company details error:", err);
        setError(err.message || "Unable to load company details.");
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [companyId, selectedDriveId]
  );

  useEffect(() => {
    loadCompanyDetails();
  }, [loadCompanyDetails]);

  /*
   * Automatically opens the browser print dialog when opened with ?print=true.
   */
  useEffect(() => {
    if (searchParams.get("print") === "true" && !loading && details) {
      const timer = setTimeout(() => {
        window.print();
      }, 700);
      return () => clearTimeout(timer);
    }
  }, [searchParams, loading, details]);

  const data = details || {};
  const companyName = company?.name || data.company || "Company";
  const industry = company?.industry || data.industry || "Information Technology";
  const rawWeb = company?.website || data.website || null;

  const website = getCompanyWebsite(company || { name: companyName, website: rawWeb });

  const handleDownloadReport = () => {
    generateCompanyPdfReport(data, company, website, rounds);
  };
  const recruitmentDate = data.recruitment_date;
  const jobRole = data.job_role;
  const overallDifficulty = data.difficulty;
  const eligibility = data.eligibility || {};

  const cgpa = eligibility.minimum_cgpa;
  const maximumBacklogs = eligibility.maximum_backlogs;
  const branchEligibility = eligibility.branch_eligibility;
  const otherCriteria = eligibility.other_criteria;

  // Real ordered rounds from database
  const rounds = useMemo(() => {
    return processRounds(data.rounds);
  }, [data.rounds]);

  // Topics sorted by occurrence count
  const topics = useMemo(() => {
    if (!Array.isArray(data.topics)) return [];
    return [...data.topics]
      .filter((t) => t && (t.topic || t.name))
      .map((t) => ({
        id: t.id,
        topic: t.topic || t.name,
        category: t.category || "Technical",
        occurrence_count: Number(t.occurrence_count || t.count || 1),
      }))
      .sort((a, b) => b.occurrence_count - a.occurrence_count);
  }, [data.topics]);

  // Cleaned and deduplicated questions
  const uniqueQuestions = useMemo(() => {
    const rawQuestions = Array.isArray(data.frequent_questions)
      ? data.frequent_questions
      : [];

    const list = [];
    const seen = new Set();

    for (const q of rawQuestions) {
      const rawText = q.question || q.question_text || "";
      const cleaned = cleanQuestionText(rawText);
      if (!cleaned) continue;

      const normKey = cleaned.toLowerCase().replace(/[^a-z0-9]/g, "");
      if (!seen.has(normKey)) {
        seen.add(normKey);
        list.push({
          ...q,
          cleanedQuestion: cleaned,
          occurrence_count: Number(q.occurrence_count || 1),
        });
      }
    }

    return list.sort((a, b) => b.occurrence_count - a.occurrence_count);
  }, [data.frequent_questions]);

  // Difficulty metrics from questions and rounds
  const difficultyStats = useMemo(() => {
    let easy = 0;
    let medium = 0;
    let hard = 0;

    uniqueQuestions.forEach((q) => {
      const diff = (q.difficulty || "").toLowerCase();
      if (diff.includes("easy")) easy++;
      else if (diff.includes("med") || diff.includes("mod")) medium++;
      else if (diff.includes("hard") || diff.includes("diff")) hard++;
    });

    // If questions didn't provide difficulty ratings, extract from rounds
    if (easy === 0 && medium === 0 && hard === 0 && rounds.length > 0) {
      rounds.forEach((r) => {
        const diff = (r.difficulty || "").toLowerCase();
        if (diff.includes("easy")) easy++;
        else if (diff.includes("med") || diff.includes("mod")) medium++;
        else if (diff.includes("hard") || diff.includes("diff")) hard++;
      });
    }

    const total = easy + medium + hard;

    const chartData = [
      { name: "Easy", count: easy, color: "#10b981" },
      { name: "Medium", count: medium, color: "#4f46e5" },
      { name: "Hard", count: hard, color: "#ef4444" },
    ];

    return { easy, medium, hard, total, chartData };
  }, [uniqueQuestions, rounds]);

  // Factual Placement Insights derived strictly from actual data
  const placementInsights = useMemo(() => {
    const insights = [];

    // 1. Top topic focus
    if (topics.length > 0) {
      const topTopic = topics[0];
      insights.push({
        icon: <Code2 size={18} />,
        title: "Primary Technical Focus",
        text: `"${topTopic.topic}" is the most frequently discussed topic with ${topTopic.occurrence_count} reported discussion${topTopic.occurrence_count === 1 ? "" : "s"}.`,
      });
    }

    // 2. Question volume
    if (uniqueQuestions.length > 0) {
      const repeatedQuestions = uniqueQuestions.filter(
        (q) => q.occurrence_count > 1
      );
      insights.push({
        icon: <MessageSquareText size={18} />,
        title: "Interview Question Volume",
        text: `${uniqueQuestions.length} distinct interview question${uniqueQuestions.length === 1 ? "" : "s"} extracted from placement feedback${repeatedQuestions.length > 0 ? `, with ${repeatedQuestions.length} repeated across candidates` : ""}.`,
      });
    }

    // 3. Recruitment process breadth
    if (rounds.length > 0) {
      const stageTypes = rounds
        .map((r) => r.round_type)
        .filter(Boolean)
        .slice(0, 4)
        .join(" → ");
      insights.push({
        icon: <Layers3 size={18} />,
        title: "Recruitment Progression",
        text: `${rounds.length} sequential round${rounds.length === 1 ? "" : "s"} identified: ${stageTypes || "Assessment and interviews"}.`,
      });
    }

    // 4. Evaluated difficulty tendency
    if (overallDifficulty || difficultyStats.total > 0) {
      const dominant =
        overallDifficulty ||
        (difficultyStats.hard >= difficultyStats.medium &&
        difficultyStats.hard >= difficultyStats.easy
          ? "Hard"
          : difficultyStats.medium >= difficultyStats.easy
          ? "Medium"
          : "Easy");

      insights.push({
        icon: <Target size={18} />,
        title: "Evaluated Difficulty",
        text: `Feedback indicates an overall ${dominant} difficulty level based on candidate responses.`,
      });
    }

    // 5. Eligibility requirement
    if (cgpa !== undefined && cgpa !== null) {
      insights.push({
        icon: <GraduationCap size={18} />,
        title: "Reported Eligibility",
        text: `Reported threshold requires ${cgpa} minimum CGPA${maximumBacklogs !== null && maximumBacklogs !== undefined ? ` and ${maximumBacklogs === 0 ? "zero active backlogs" : `maximum ${maximumBacklogs} backlog(s)`}` : ""}.`,
      });
    }

    // 6. Confidence & reliability
    const questionsWithConfidence = uniqueQuestions.filter(
      (q) => typeof q.confidence_score === "number" && q.confidence_score > 0
    );
    if (questionsWithConfidence.length > 0) {
      const avgConfidence = Math.round(
        questionsWithConfidence.reduce(
          (sum, q) => sum + q.confidence_score,
          0
        ) / questionsWithConfidence.length
      );
      insights.push({
        icon: <ShieldCheck size={18} />,
        title: "Extraction Confidence",
        text: `Extracted interview items demonstrate a ${avgConfidence}% average AI reliability score.`,
      });
    }

    return insights;
  }, [
    topics,
    uniqueQuestions,
    rounds,
    overallDifficulty,
    difficultyStats,
    cgpa,
    maximumBacklogs,
  ]);

  if (loading) {
    return (
      <main className="company-details-page">
        <div className="company-details-container company-details-loading">
          <Loader2 size={32} className="company-details-spin" />
          <p>Loading company intelligence...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="company-details-page">
        <div className="company-details-container">
          <div className="company-details-actions">
            <Link to="/companies" className="details-back-link">
              <ArrowLeft size={16} />
              Back to Companies
            </Link>
          </div>

          <section className="company-details-error">
            <CircleAlert size={36} />
            <h2>Unable to load company intelligence</h2>
            <p>{error}</p>
            <button
              type="button"
              onClick={() => loadCompanyDetails()}
              className="details-report-button"
              style={{ marginTop: "16px" }}
            >
              Try Again
            </button>
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="company-details-page">
      <div className="company-details-container">
        {/* 1. TOP ACTIONS */}
        <div className="company-details-actions">
          <Link to="/companies" className="details-back-link">
            <ArrowLeft size={16} />
            Back to Companies
          </Link>

          <div className="company-details-action-buttons">
            <button
              type="button"
              className="details-report-button"
              onClick={handleDownloadReport}
              title="Print or export company placement report"
            >
              <FileDown size={16} />
              Download Report
            </button>

            <button
              type="button"
              className="details-refresh-button"
              onClick={() => loadCompanyDetails(true)}
              disabled={refreshing}
              title="Refresh company intelligence"
            >
              <RefreshCw
                size={16}
                className={refreshing ? "company-details-spin" : ""}
              />
              {refreshing ? "Refreshing..." : "Refresh"}
            </button>
          </div>
        </div>

        {/* 1. COMPANY HEADER / HERO */}
        <section className="company-hero">
          <div className="company-hero-logo">
            {companyName.charAt(0).toUpperCase()}
          </div>

          <div className="company-hero-content">
            <div className="details-eyebrow">
              <Sparkles size={14} />
              Company Intelligence Dashboard
            </div>

            <h1>{companyName}</h1>

            <div className="company-hero-meta">
              <span>
                <Building2 size={15} />
                {industry}
              </span>

              {website ? (
                <a
                  href={website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="company-hero-website-btn"
                  title={`Visit ${companyName} official website`}
                >
                  <ExternalLink size={14} />
                  <span>Visit Website</span>
                </a>
              ) : (
                <span className="company-hero-website-disabled">
                  <ExternalLink size={14} />
                  <span>Website Unavailable</span>
                </span>
              )}

              <span>
                <Trophy size={14} />
                {data.placement_drives || 1} Placement Drive
                {(data.placement_drives || 1) === 1 ? "" : "s"} Analyzed
              </span>
            </div>
          </div>
        </section>

        {Array.isArray(data.available_drives) &&
          data.available_drives.length > 1 && (
            <section className="company-drive-selector">
              <label htmlFor="company-drive-select">Placement drive</label>
              <select
                id="company-drive-select"
                value={String(data.drive_id ?? "")}
                onChange={(event) => {
                  const nextParams = new URLSearchParams(searchParams);
                  nextParams.set("drive_id", event.target.value);
                  setSearchParams(nextParams);
                }}
              >
                {data.available_drives.map((drive) => {
                  const label = [
                    drive.job_role || "Role not specified",
                    drive.batch ? `Batch ${drive.batch}` : null,
                    drive.year,
                    drive.package ? `Package ${drive.package}` : null,
                    drive.recruitment_date
                      ? formatDate(drive.recruitment_date)
                      : null,
                    `Drive #${drive.id}`,
                  ]
                    .filter(Boolean)
                    .join(" · ");

                  return (
                    <option key={drive.id} value={String(drive.id)}>
                      {label}
                    </option>
                  );
                })}
              </select>
            </section>
          )}

        {/* 2. PLACEMENT OVERVIEW STATS */}
        <section className="details-stats-grid">
          <article className="details-stat-card">
            <div className="details-stat-icon purple">
              <CalendarDays size={20} />
            </div>
            <div>
              <span>Recruitment Date</span>
              <strong>{formatDate(recruitmentDate)}</strong>
            </div>
          </article>

          <article className="details-stat-card">
            <div className="details-stat-icon blue">
              <BriefcaseBusiness size={20} />
            </div>
            <div>
              <span>Target Role</span>
              <strong>{displayValue(jobRole, "Software Engineer / Graduate Trainee")}</strong>
            </div>
          </article>

          <article className="details-stat-card">
            <div className="details-stat-icon green">
              <Layers3 size={20} />
            </div>
            <div>
              <span>Recruitment Rounds</span>
              <strong>
                {rounds.length > 0 ? `${rounds.length} Stages` : "Not reported"}
              </strong>
            </div>
          </article>

          <article className="details-stat-card">
            <div className="details-stat-icon orange">
              <Target size={20} />
            </div>
            <div>
              <span>Overall Difficulty</span>
              <strong>{displayValue(overallDifficulty, "Medium (Evaluated)")}</strong>
            </div>
          </article>
        </section>

        {/* 2b. ELIGIBILITY INFORMATION */}
        <section className="details-section">
          <div className="details-section-heading">
            <div className="details-section-icon">
              <GraduationCap size={19} />
            </div>
            <div>
              <h2>Reported Eligibility Criteria</h2>
              <p>Academic requirements extracted from placement feedback records</p>
            </div>
          </div>

          <div className="eligibility-grid">
            <div className="eligibility-card">
              <span>Reported Minimum CGPA</span>
              <strong>
                {cgpa !== null && cgpa !== undefined ? `${cgpa} CGPA` : "Not specified"}
              </strong>
            </div>

            <div className="eligibility-card">
              <span>Backlog Criteria</span>
              <strong>
                {maximumBacklogs === 0
                  ? "No active backlogs allowed"
                  : maximumBacklogs !== null && maximumBacklogs !== undefined
                  ? `Max ${maximumBacklogs} backlog(s)`
                  : "Not specified"}
              </strong>
            </div>

            <div className="eligibility-card">
              <span>Eligible Branches</span>
              <strong>
                {displayValue(branchEligibility, "B.E. CSE / IT / Circuit Branches")}
              </strong>
            </div>

            <div className="eligibility-card">
              <span>Drive Status</span>
              <strong>Batch 2023–2027 Recruitment Cycle</strong>
            </div>

            {otherCriteria && (
              <div className="eligibility-description">
                <CheckCircle2 size={17} />
                <span>{otherCriteria}</span>
              </div>
            )}

            <div className="eligibility-disclaimer">
              <AlertCircle size={15} />
              <span>
                Reported values reflect candidate feedback submissions and should be confirmed with the placement office.
              </span>
            </div>
          </div>
        </section>

        {/* 7. PLACEMENT INSIGHTS */}
        {placementInsights.length > 0 && (
          <section className="details-section">
            <div className="details-section-heading">
              <div className="details-section-icon">
                <Brain size={19} />
              </div>
              <div>
                <h2>Placement Intelligence Insights</h2>
                <p>Data-driven findings synthesized from authorized candidate submissions</p>
              </div>
            </div>

            <div className="details-insights-grid">
              {placementInsights.map((insight, index) => (
                <div className="details-insight-card" key={index}>
                  <div className="details-insight-icon">{insight.icon}</div>
                  <div className="details-insight-body">
                    <h4>{insight.title}</h4>
                    <p>{insight.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* TWO-COLUMN GRID: 4. TECHNICAL TOPICS & 6. DIFFICULTY DISTRIBUTION */}
        <div className="details-grid-two-col">
          {/* 4. TECHNICAL TOPICS */}
          <section className="details-section" style={{ marginTop: 0 }}>
            <div className="details-section-heading">
              <div className="details-section-icon">
                <Code2 size={19} />
              </div>
              <div>
                <h2>Technical Topics</h2>
                <p>Subjects tested in assessments and interviews</p>
              </div>
            </div>

            {topics.length > 0 ? (
              <div className="topics-enhanced-list">
                {topics.map((t, idx) => (
                  <div className="topic-chip-enhanced" key={idx}>
                    <div className="topic-chip-left">
                      <span className="topic-chip-name">{t.topic}</span>
                      <span className="topic-chip-category">{t.category}</span>
                    </div>

                    <span className="topic-chip-count">
                      {t.occurrence_count}{" "}
                      {t.occurrence_count === 1 ? "mention" : "mentions"}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="details-empty">
                <Code2 size={22} />
                <p>No technical topics recorded for this company yet.</p>
              </div>
            )}
          </section>

          {/* 6. DIFFICULTY DISTRIBUTION */}
          <section className="details-section" style={{ marginTop: 0 }}>
            <div className="details-section-heading">
              <div className="details-section-icon">
                <BarChart2 size={19} />
              </div>
              <div>
                <h2>Difficulty Distribution</h2>
                <p>Question and round difficulty breakdown</p>
              </div>
            </div>

            {difficultyStats.total > 0 ? (
              <div className="difficulty-chart-box">
                <div style={{ width: "100%", height: 180 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={difficultyStats.chartData}
                      layout="vertical"
                      margin={{ top: 10, right: 24, left: 10, bottom: 0 }}
                    >
                      <XAxis type="number" allowDecimals={false} hide />
                      <YAxis
                        dataKey="name"
                        type="category"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: "#374151", fontSize: 13, fontWeight: 600 }}
                        width={68}
                      />
                      <Tooltip content={<DifficultyTooltip />} />
                      <Bar
                        dataKey="count"
                        radius={[0, 8, 8, 0]}
                        barSize={20}
                      >
                        {difficultyStats.chartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="difficulty-legend">
                  <div className="difficulty-legend-item">
                    <span
                      className="difficulty-legend-dot"
                      style={{ background: "#10b981" }}
                    />
                    <span>Easy</span>
                    <span className="difficulty-legend-badge">
                      {difficultyStats.easy} (
                      {Math.round(
                        (difficultyStats.easy / difficultyStats.total) * 100
                      )}
                      %)
                    </span>
                  </div>

                  <div className="difficulty-legend-item">
                    <span
                      className="difficulty-legend-dot"
                      style={{ background: "#4f46e5" }}
                    />
                    <span>Medium</span>
                    <span className="difficulty-legend-badge">
                      {difficultyStats.medium} (
                      {Math.round(
                        (difficultyStats.medium / difficultyStats.total) * 100
                      )}
                      %)
                    </span>
                  </div>

                  <div className="difficulty-legend-item">
                    <span
                      className="difficulty-legend-dot"
                      style={{ background: "#ef4444" }}
                    />
                    <span>Hard</span>
                    <span className="difficulty-legend-badge">
                      {difficultyStats.hard} (
                      {Math.round(
                        (difficultyStats.hard / difficultyStats.total) * 100
                      )}
                      %)
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="details-empty">
                <Target size={22} />
                <p>No difficulty ratings recorded in feedback yet.</p>
              </div>
            )}
          </section>
        </div>

        {/* 3. RECRUITMENT PROCESS */}
        <section className="details-section">
          <div className="details-section-heading">
            <div className="details-section-icon">
              <Layers3 size={19} />
            </div>
            <div>
              <h2>Recruitment Process</h2>
              <p>Sequential rounds extracted from verified placement feedback</p>
            </div>
          </div>

          {rounds.length > 0 ? (
            <div className="rounds-list">
              {rounds.map((round, index) => {
                const diffLower = (round.difficulty || "").toLowerCase();
                const diffClass = diffLower.includes("easy")
                  ? "easy"
                  : diffLower.includes("hard")
                  ? "hard"
                  : "medium";

                return (
                  <article className="round-card" key={index}>
                    <div className="round-number">{index + 1}</div>

                    <div className="round-content">
                      <h3>{round.round_type || `Round ${index + 1}`}</h3>
                      <span>
                        {round.description || "Assessment / Interview Stage"}
                      </span>
                      {round.difficulty && (
                        <div>
                          <span className={`round-difficulty-tag ${diffClass}`}>
                            {round.difficulty}
                          </span>
                        </div>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          ) : (
            <div className="details-empty">
              <Layers3 size={22} />
              <p>No recruitment round details recorded for this company yet.</p>
            </div>
          )}
        </section>

        <InterviewPreparationRoadmap
          key={`${companyId}:${data.drive_id ?? "none"}`}
          companyId={companyId}
          driveId={data.drive_id}
          companyName={companyName}
          jobRole={data.job_role}
          rounds={data.rounds}
          topics={data.topics}
          preparationTopics={data.preparation_topics}
          questions={data.frequent_questions}
          eligibility={data.eligibility}
        />

        {/* 5. FREQUENTLY ASKED QUESTIONS */}
        <section className="details-section questions-section">
          <div className="details-section-heading">
            <div className="details-section-icon">
              <MessageSquareText size={19} />
            </div>
            <div>
              <h2>Frequently Asked Questions</h2>
              <p>Interview questions reported by students who attended this drive</p>
            </div>
            <div className="questions-count">
              {uniqueQuestions.length} unique question
              {uniqueQuestions.length === 1 ? "" : "s"}
            </div>
          </div>

          {uniqueQuestions.length > 0 ? (
            <div className="questions-list">
              {uniqueQuestions.map((q, index) => {
                const diffLower = (q.difficulty || "").toLowerCase();
                const diffClass = diffLower.includes("easy")
                  ? "easy"
                  : diffLower.includes("hard")
                  ? "hard"
                  : "medium";

                return (
                  <article className="question-card" key={q.id || index}>
                    <div className="question-number">{index + 1}</div>

                    <div className="question-content">
                      <h3>{q.cleanedQuestion}</h3>

                      <div className="question-meta">
                        <span>
                          Reported {q.occurrence_count} time
                          {q.occurrence_count === 1 ? "" : "s"}
                        </span>

                        {q.difficulty && (
                          <span
                            className={`question-badge-difficulty ${diffClass}`}
                          >
                            {q.difficulty}
                          </span>
                        )}

                        {q.confidence_score && (
                          <span className="question-badge-confidence">
                            <Sparkles size={11} />
                            {Math.round(q.confidence_score)}% confidence
                          </span>
                        )}

                        {q.verification_status && (
                          <span
                            className={
                              q.verification_status === "verified"
                                ? "question-badge-verified"
                                : "question-badge-unverified"
                            }
                          >
                            {q.verification_status === "verified" ? (
                              <>
                                <CheckCircle2 size={11} />
                                Verified
                              </>
                            ) : (
                              "Feedback Reported"
                            )}
                          </span>
                        )}
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          ) : (
            <div className="details-empty">
              <HelpCircle size={22} />
              <p>No interview questions recorded for this company yet.</p>
            </div>
          )}
        </section>

        {/* FOOTER */}
        <section className="company-details-footer">
          <Users size={18} />
          <span>
            Placement Intelligence Dashboard • 2023–2027 CSE Placement Cycle • Derived from authorized feedback
          </span>
        </section>

        {/* PRINTABLE SUMMARY REPORT (Hidden on screen, shown when printing) */}
        <div className="printable-report-container print-report-only">
          <header className="report-header">
            <div className="report-header-title">
              <h1>PLACEMENT INTELLIGENCE — COMPANY REPORT</h1>
              <p>Official Placement Summary Document • Batch 2023–2027 CSE Placement Cycle</p>
            </div>
            <div className="report-header-meta">
              <span>Date: {new Date().toLocaleDateString("en-IN")}</span>
              <span>System Verified Data</span>
            </div>
          </header>

          <hr className="report-divider" />

          {/* 1. Company Overview */}
          <section className="report-section">
            <h2>1. Company Overview</h2>
            <table className="report-table">
              <tbody>
                <tr>
                  <th>Company Name</th>
                  <td>{companyName}</td>
                  <th>Industry</th>
                  <td>{industry}</td>
                </tr>
                <tr>
                  <th>Official Website</th>
                  <td>{website ? website : "Not available"}</td>
                  <th>Placement Drives Analyzed</th>
                  <td>{data.placement_drives || 1} Drive(s)</td>
                </tr>
                <tr>
                  <th>Recruitment Date</th>
                  <td>{formatDate(recruitmentDate)}</td>
                  <th>Target Job Role</th>
                  <td>{displayValue(jobRole, "Software Engineer / Graduate Trainee")}</td>
                </tr>
              </tbody>
            </table>
          </section>

          {/* 2. Eligibility */}
          <section className="report-section">
            <h2>2. Eligibility Criteria</h2>
            <table className="report-table">
              <tbody>
                <tr>
                  <th>Minimum CGPA</th>
                  <td>{cgpa !== null && cgpa !== undefined ? `${cgpa} CGPA` : "Not specified"}</td>
                  <th>Backlog Requirement</th>
                  <td>
                    {maximumBacklogs === 0
                      ? "No active backlogs allowed"
                      : maximumBacklogs !== null && maximumBacklogs !== undefined
                      ? `Max ${maximumBacklogs} backlog(s)`
                      : "Not specified"}
                  </td>
                </tr>
                <tr>
                  <th>Eligible Branches</th>
                  <td>{displayValue(branchEligibility, "B.E. CSE / IT / Circuit Branches")}</td>
                  <th>Batch / Drive Cycle</th>
                  <td>2023–2027 CSE Batch Cycle</td>
                </tr>
              </tbody>
            </table>
          </section>

          {/* 3. Recruitment Process */}
          <section className="report-section">
            <h2>3. Recruitment Process Structure</h2>
            <p className="report-text">
              Total Sequential Rounds: <strong>{rounds.length} Stage(s)</strong>
            </p>
            {rounds.length > 0 ? (
              <table className="report-table">
                <thead>
                  <tr>
                    <th>Round #</th>
                    <th>Stage Name</th>
                    <th>Description</th>
                    <th>Difficulty Rating</th>
                  </tr>
                </thead>
                <tbody>
                  {rounds.map((r, i) => (
                    <tr key={i}>
                      <td>Round {i + 1}</td>
                      <td>{r.round_type || `Round ${i + 1}`}</td>
                      <td>{r.description || "Assessment stage"}</td>
                      <td>{r.difficulty || "Medium"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="report-text-muted">No specific recruitment rounds recorded.</p>
            )}
          </section>

          {/* 4. Technical Intelligence */}
          <section className="report-section">
            <h2>4. Technical Intelligence</h2>
            {topics.length > 0 ? (
              <div className="report-tags-wrapper">
                {topics.map((t, i) => (
                  <span key={i} className="report-tag">
                    {t.topic} ({t.occurrence_count} mention{t.occurrence_count === 1 ? "" : "s"})
                  </span>
                ))}
              </div>
            ) : (
              <p className="report-text-muted">No technical topics recorded.</p>
            )}
          </section>

          {/* 5. Question Intelligence */}
          <section className="report-section">
            <h2>5. Question Intelligence</h2>
            {uniqueQuestions.length > 0 ? (
              <table className="report-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Question Text</th>
                    <th>Frequency</th>
                    <th>Difficulty</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {uniqueQuestions.slice(0, 10).map((q, i) => (
                    <tr key={i}>
                      <td>{i + 1}</td>
                      <td>{q.cleanedQuestion}</td>
                      <td>{q.occurrence_count} time(s)</td>
                      <td>{q.difficulty || "Medium"}</td>
                      <td>{q.confidence_score ? `${Math.round(q.confidence_score)}%` : "N/A"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="report-text-muted">No interview questions recorded.</p>
            )}
          </section>

          {/* 6. Difficulty Summary */}
          <section className="report-section">
            <h2>6. Difficulty Summary</h2>
            <table className="report-table">
              <tbody>
                <tr>
                  <th>Overall Evaluated Level</th>
                  <td>{displayValue(overallDifficulty, "Medium")}</td>
                  <th>Easy Questions</th>
                  <td>{difficultyStats.easy} ({difficultyStats.total > 0 ? Math.round((difficultyStats.easy / difficultyStats.total) * 100) : 0}%)</td>
                </tr>
                <tr>
                  <th>Medium Questions</th>
                  <td>{difficultyStats.medium} ({difficultyStats.total > 0 ? Math.round((difficultyStats.medium / difficultyStats.total) * 100) : 0}%)</td>
                  <th>Hard Questions</th>
                  <td>{difficultyStats.hard} ({difficultyStats.total > 0 ? Math.round((difficultyStats.hard / difficultyStats.total) * 100) : 0}%)</td>
                </tr>
              </tbody>
            </table>
          </section>

          {/* 7. Confidence / Verification */}
          <section className="report-section">
            <h2>7. Data Confidence & Verification</h2>
            <p className="report-text">
              Extracted feedback items demonstrate an average system confidence score derived from NLP linguistic verification models. All data items originated from authorized candidate submission channels.
            </p>
          </section>

          {/* 8. Key Placement Insights */}
          <section className="report-section">
            <h2>8. Key Placement Insights</h2>
            <ul className="report-list">
              {placementInsights.map((insight, i) => (
                <li key={i}>
                  <strong>{insight.title}:</strong> {insight.text}
                </li>
              ))}
            </ul>
          </section>

          <footer className="report-footer">
            <span>Generated by Placement Feedback Intelligence System</span>
            <span>Final Year CSE Engineering Capstone Project</span>
          </footer>
        </div>
      </div>
    </main>
  );
}

export default CompanyDetails;
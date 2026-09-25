import { useEffect, useState } from "react";

import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import {
  BarChart3,
  Brain,
  Building2,
  RefreshCw,
  MessageSquare,
  Layers3,
  Target,
  TrendingUp,
  Code2,
  Database,
  Trophy,
  HelpCircle,
  CheckCircle2,
  FileDown,
} from "lucide-react";

const API = "/api";

const CATEGORY_COLORS = [
  "#4f46e5",
  "#0f766e",
  "#7c3aed",
  "#2563eb",
  "#0891b2",
];

async function getData(endpoint) {
  const response = await fetch(API + endpoint);

  if (!response.ok) {
    throw new Error("API request failed: " + endpoint);
  }

  return response.json();
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}

function cleanText(value) {
  return String(value || "")
    .replace(/\*\*/g, "")
    .replace(/__/g, "")
    .trim();
}

function getTopicData(data) {
  if (!Array.isArray(data)) {
    return [];
  }

  return data
    .filter((item) => item && item.topic)
    .map((item) => ({
      name: cleanText(item.topic),
      count: Number(
        item.occurrence_count || item.count || 0
      ),
    }))
    .filter((item) => item.name && item.count > 0)
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);
}

function getCategoryData(data) {
  if (!Array.isArray(data)) {
    return [];
  }

  return data
    .filter((item) => item && item.category)
    .map((item) => ({
      name: cleanText(item.category),
      value: Number(
        item.occurrence_count || item.count || 0
      ),
    }))
    .filter((item) => item.name && item.value > 0);
}

function getQuestionData(data) {
  if (!Array.isArray(data)) {
    return [];
  }

  return data
    .map((item) => {
      const question =
        item.question_text ||
        item.question ||
        item.text ||
        "";

      const count = Number(
        item.occurrence_count ||
          item.count ||
          item.frequency ||
          0
      );

      return {
        question: cleanText(question),
        count,
      };
    })
    .filter(
      (item) => item.question && item.count > 0
    )
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);
}

function getEligibilityData(data) {
  if (!data) {
    return [];
  }

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.data)) {
    return data.data;
  }

  return [];
}

function TopicTooltip({ active, payload }) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const item = payload[0].payload;

  return (
    <div className="analytics-tooltip">
      <p>{item.name}</p>
      <strong>{item.count} discussions</strong>
    </div>
  );
}

function CategoryTooltip({ active, payload }) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const item = payload[0].payload;

  return (
    <div className="analytics-tooltip">
      <p>{item.name}</p>
      <strong>{item.value} discussions</strong>
    </div>
  );
}

function Analytics() {
  const [overview, setOverview] = useState(null);
  const [topics, setTopics] = useState([]);
  const [categories, setCategories] = useState([]);
  const [confidence, setConfidence] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [eligibility, setEligibility] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const handleDownloadReport = () => {
    window.print();
  };

  async function loadAnalytics(isRefresh = false) {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError("");

    const results = await Promise.allSettled([
      getData("/analytics/overview"),
      getData("/analytics/frequent-topics"),
      getData("/analytics/categories"),
      getData("/analytics/confidence"),
      getData("/analytics/frequent-questions"),
      getData("/analytics/eligibility"),
    ]);

    const [
      overviewResult,
      topicsResult,
      categoriesResult,
      confidenceResult,
      questionsResult,
      eligibilityResult,
    ] = results;

    if (overviewResult.status === "fulfilled") {
      setOverview(overviewResult.value);
    }

    if (topicsResult.status === "fulfilled") {
      setTopics(
        getTopicData(topicsResult.value)
      );
    }

    if (categoriesResult.status === "fulfilled") {
      setCategories(
        getCategoryData(categoriesResult.value)
      );
    }

    if (confidenceResult.status === "fulfilled") {
      setConfidence(confidenceResult.value);
    }

    if (questionsResult.status === "fulfilled") {
      setQuestions(
        getQuestionData(questionsResult.value)
      );
    }

    if (eligibilityResult.status === "fulfilled") {
      setEligibility(
        getEligibilityData(eligibilityResult.value)
      );
    }

    const failed = results.some(
      (result) => result.status === "rejected"
    );

    if (failed) {
      setError(
        "Some analytics data could not be loaded. Available data is still displayed."
      );
    }

    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => {
    loadAnalytics();
  }, []);

  const totalCompanies = Number(
    overview?.total_companies || 0
  );

  const totalDrives = Number(
    overview?.total_placement_drives || 0
  );

  const totalQuestions = Number(
    overview?.total_questions || 0
  );

  const totalTopics = Number(
    overview?.total_topics || 0
  );

  const totalRounds = Number(
    overview?.total_recruitment_rounds || 0
  );

  const averageConfidence = Math.min(
    Math.max(
      Number(
        confidence?.average_confidence || 0
      ),
      0
    ),
    100
  );

  const topTopic =
    topics.length > 0 ? topics[0] : null;

  /*
   * Group eligibility records by company.
   * This prevents repeated company cards.
   */
  const groupedEligibility = Object.values(
    eligibility.reduce((groups, item) => {
      const companyName = cleanText(
        item.company_name ||
          item.company ||
          "Company"
      );

      if (!groups[companyName]) {
        groups[companyName] = [];
      }

      groups[companyName].push(item);

      return groups;
    }, {})
  );

  return (
    <main className="analytics-page">
      <div className="analytics-container">

        {/* PAGE HEADER */}

        <header className="analytics-page-header">
          <div className="analytics-heading-area">

            <div className="analytics-eyebrow">
              <BarChart3 size={16} />
              Placement Intelligence
            </div>

            <h1>Analytics Dashboard</h1>

            <p>
              Transform placement feedback into
              meaningful recruitment insights.
            </p>

          </div>

          <div className="analytics-header-actions">

            <button
              type="button"
              className="analytics-report-button"
              onClick={handleDownloadReport}
            >
              <FileDown size={16} />
              Download Report
            </button>

            <button
              type="button"
              className="analytics-refresh"
              onClick={() => loadAnalytics(true)}
              disabled={refreshing}
            >
              <RefreshCw
                size={17}
                className={
                  refreshing
                    ? "analytics-spin"
                    : ""
                }
              />

              {refreshing
                ? "Refreshing..."
                : "Refresh Data"}
            </button>

          </div>
        </header>

        {/* WARNING */}

        {error && (
          <div className="analytics-warning">
            <Brain size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* LOADING */}

        {loading ? (
          <div className="analytics-loading">
            <RefreshCw
              className="analytics-spin"
              size={30}
            />

            <p>
              Loading placement intelligence...
            </p>
          </div>
        ) : (
          <>

            {/* TOP STATISTICS */}

            <section className="analytics-stats-grid">

              <div className="analytics-stat-card">
                <div className="analytics-stat-icon purple">
                  <Building2 size={22} />
                </div>

                <div className="analytics-stat-content">
                  <span>Companies</span>

                  <strong>
                    {formatNumber(totalCompanies)}
                  </strong>

                  <small>
                    Companies analyzed
                  </small>
                </div>
              </div>

              <div className="analytics-stat-card">
                <div className="analytics-stat-icon blue">
                  <Trophy size={22} />
                </div>

                <div className="analytics-stat-content">
                  <span>Placement Drives</span>

                  <strong>
                    {formatNumber(totalDrives)}
                  </strong>

                  <small>
                    Recruitment drives
                  </small>
                </div>
              </div>

              <div className="analytics-stat-card">
                <div className="analytics-stat-icon teal">
                  <MessageSquare size={22} />
                </div>

                <div className="analytics-stat-content">
                  <span>Questions</span>

                  <strong>
                    {formatNumber(totalQuestions)}
                  </strong>

                  <small>
                    Questions analyzed
                  </small>
                </div>
              </div>

              <div className="analytics-stat-card">
                <div className="analytics-stat-icon orange">
                  <Layers3 size={22} />
                </div>

                <div className="analytics-stat-content">
                  <span>Topics</span>

                  <strong>
                    {formatNumber(totalTopics)}
                  </strong>

                  <small>
                    Topics identified
                  </small>
                </div>
              </div>

            </section>

            {/* TOPICS + CATEGORIES */}

            <section className="analytics-section">

              <div className="analytics-section-header">

                <div className="analytics-section-icon">
                  <TrendingUp size={20} />
                </div>

                <div>
                  <h2>
                    Feedback Intelligence
                  </h2>

                  <p>
                    Explore the subjects and categories
                    appearing most often in placement
                    feedback.
                  </p>
                </div>

              </div>

              <div className="analytics-two-column">

                {/* TOPICS */}

                <div className="analytics-panel">

                  <div className="analytics-panel-heading">

                    <div>
                      <h3>
                        Frequently Discussed Topics
                      </h3>

                      <p>
                        Top topics identified from
                        analyzed feedback
                      </p>
                    </div>

                    <span className="analytics-badge">
                      {topics.length} topics
                    </span>

                  </div>

                  {topics.length > 0 ? (
                    <div className="analytics-chart-box topic-chart">

                      <ResponsiveContainer
                        width="100%"
                        height={350}
                      >
                        <BarChart
                          data={topics}
                          layout="vertical"
                          margin={{
                            top: 10,
                            right: 25,
                            left: 10,
                            bottom: 10,
                          }}
                        >

                          <CartesianGrid
                            strokeDasharray="3 3"
                            horizontal={false}
                          />

                          <XAxis
                            type="number"
                            allowDecimals={false}
                          />

                          <YAxis
                            type="category"
                            dataKey="name"
                            width={90}
                            tick={{
                              fontSize: 12,
                            }}
                          />

                          <Tooltip
                            content={
                              <TopicTooltip />
                            }
                          />

                          <Bar
                            dataKey="count"
                            fill="#4f46e5"
                            radius={[
                              0,
                              7,
                              7,
                              0,
                            ]}
                            barSize={25}
                          />

                        </BarChart>
                      </ResponsiveContainer>

                    </div>
                  ) : (
                    <div className="analytics-empty">
                      <Database size={28} />

                      <p>
                        No topic data available.
                      </p>
                    </div>
                  )}

                </div>

                {/* CATEGORIES */}

                <div className="analytics-panel">

                  <div className="analytics-panel-heading">

                    <div>
                      <h3>
                        Feedback Categories
                      </h3>

                      <p>
                        Distribution of analyzed
                        feedback
                      </p>
                    </div>

                    <span className="analytics-badge">
                      {categories.length} categories
                    </span>

                  </div>

                  {categories.length > 0 ? (
                    <div className="analytics-chart-box category-chart">

                      <ResponsiveContainer
                        width="100%"
                        height={300}
                      >
                        <PieChart>

                          <Pie
                            data={categories}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            innerRadius={65}
                            outerRadius={105}
                            paddingAngle={4}
                          >

                            {categories.map(
                              (item, index) => (
                                <Cell
                                  key={item.name}
                                  fill={
                                    CATEGORY_COLORS[
                                      index %
                                        CATEGORY_COLORS.length
                                    ]
                                  }
                                />
                              )
                            )}

                          </Pie>

                          <Tooltip
                            content={
                              <CategoryTooltip />
                            }
                          />

                        </PieChart>
                      </ResponsiveContainer>

                      <div className="category-legend">

                        {categories.map(
                          (item, index) => (
                            <div
                              className="category-legend-item"
                              key={item.name}
                            >

                              <span
                                className="legend-dot"
                                style={{
                                  background:
                                    CATEGORY_COLORS[
                                      index %
                                        CATEGORY_COLORS.length
                                    ],
                                }}
                              />

                              <span>
                                {item.name}
                              </span>

                              <strong>
                                {item.value}
                              </strong>

                            </div>
                          )
                        )}

                      </div>

                    </div>
                  ) : (
                    <div className="analytics-empty">
                      <Code2 size={28} />

                      <p>
                        No category data available.
                      </p>
                    </div>
                  )}

                </div>

              </div>
            </section>

            {/* FREQUENT QUESTIONS */}

            <section className="analytics-section">

              <div className="analytics-section-header">

                <div className="analytics-section-icon">
                  <HelpCircle size={20} />
                </div>

                <div>
                  <h2>
                    Frequently Asked Questions
                  </h2>

                  <p>
                    Questions appearing repeatedly
                    across placement feedback.
                  </p>
                </div>

              </div>

              <div className="analytics-panel">

                {questions.length > 0 ? (
                  <div className="analytics-question-list">

                    {questions.map(
                      (item, index) => (
                        <div
                          className="analytics-question-item"
                          key={`${item.question}-${index}`}
                        >

                          <div className="analytics-question-number">
                            {index + 1}
                          </div>

                          <div className="analytics-question-content">

                            <p className="analytics-question-text">
                              {item.question}
                            </p>

                            <span className="analytics-question-count">
                              Asked {item.count}{" "}
                              {item.count === 1
                                ? "time"
                                : "times"}
                            </span>

                          </div>

                        </div>
                      )
                    )}

                  </div>
                ) : (
                  <div className="analytics-empty">
                    <HelpCircle size={28} />

                    <p>
                      No frequent question data
                      available.
                    </p>
                  </div>
                )}

              </div>
            </section>

            {/* ELIGIBILITY */}

            <section className="analytics-section">

              <div className="analytics-section-header">

                <div className="analytics-section-icon">
                  <Target size={20} />
                </div>

                <div>
                  <h2>
                    Eligibility Insights
                  </h2>

                  <p>
                    Eligibility information extracted
                    from placement feedback.
                  </p>
                </div>

              </div>

              <div className="analytics-panel">

                {groupedEligibility.length > 0 ? (
                  <div className="analytics-eligibility-grid">

                    {groupedEligibility.map(
                      (companyItems, index) => {

                        const companyName =
                          cleanText(
                            companyItems[0]
                              ?.company_name ||
                              companyItems[0]
                                ?.company ||
                              "Company"
                          );

                        const cgpaValues = [
                          ...new Set(
                            companyItems
                              .map(
                                (item) =>
                                  item.minimum_cgpa ??
                                  item.min_cgpa ??
                                  item.cgpa
                              )
                              .filter(
                                (value) =>
                                  value !==
                                    undefined &&
                                  value !==
                                    null &&
                                  value !== ""
                              )
                              .map(
                                (value) =>
                                  String(value)
                              )
                          ),
                        ];

                        const backlogValues = [
                          ...new Set(
                            companyItems
                              .map(
                                (item) =>
                                  item.active_backlogs ??
                                  item.backlogs ??
                                  item.backlog_requirement
                              )
                              .filter(
                                (value) =>
                                  value !==
                                    undefined &&
                                  value !==
                                    null &&
                                  value !== ""
                              )
                              .map(
                                (value) =>
                                  String(value)
                              )
                          ),
                        ];

                        const cgpaText =
                          cgpaValues.length > 0
                            ? cgpaValues.join(", ")
                            : "Not specified";

                        const backlogText =
                          backlogValues.length > 0
                            ? backlogValues.join(", ")
                            : "Not specified";

                        return (
                          <article
                            className="analytics-eligibility-card"
                            key={`${companyName}-${index}`}
                          >

                            <div className="analytics-eligibility-top">

                              <div className="analytics-eligibility-company-icon">
                                <Building2 size={18} />
                              </div>

                              <div>
                                <h3>
                                  {companyName}
                                </h3>

                                <span>
                                  Eligibility criteria
                                </span>
                              </div>

                            </div>

                            <div className="analytics-eligibility-divider" />

                            <div className="analytics-eligibility-metrics">

                              <div className="analytics-eligibility-metric">

                                <span className="analytics-eligibility-label">
                                  Reported CGPA
                                </span>

                                <strong className="analytics-eligibility-cgpa">
                                  {cgpaText}
                                </strong>

                              </div>

                              <div className="analytics-eligibility-metric">

                                <span className="analytics-eligibility-label">
                                  Backlog requirement
                                </span>

                                <strong>
                                  {backlogText}
                                </strong>

                              </div>

                            </div>

                            <div className="analytics-eligibility-footer">
                              <CheckCircle2 size={14} />

                              <span>
                                Based on available placement
                                feedback
                              </span>
                            </div>

                          </article>
                        );
                      }
                    )}

                  </div>
                ) : (
                  <div className="analytics-empty">

                    <Target size={28} />

                    <p>
                      No eligibility information
                      available.
                    </p>

                  </div>
                )}

              </div>
            </section>

            {/* INTELLIGENCE SUMMARY */}

            <section className="analytics-section">

              <div className="analytics-section-header">

                <div className="analytics-section-icon">
                  <Brain size={20} />
                </div>

                <div>
                  <h2>
                    Intelligence Summary
                  </h2>

                  <p>
                    A quick overview of the current
                    placement feedback database.
                  </p>
                </div>

              </div>

              <div className="analytics-summary-grid">

                <div className="analytics-summary-card">

                  <div className="summary-icon">
                    <MessageSquare size={20} />
                  </div>

                  <div>
                    <span>
                      Feedback analyzed
                    </span>

                    <strong>
                      {formatNumber(
                        totalQuestions
                      )}
                    </strong>

                    <p>
                      Questions extracted from
                      placement feedback.
                    </p>
                  </div>

                </div>

                <div className="analytics-summary-card">

                  <div className="summary-icon">
                    <Layers3 size={20} />
                  </div>

                  <div>
                    <span>
                      Topics identified
                    </span>

                    <strong>
                      {formatNumber(
                        totalTopics
                      )}
                    </strong>

                    <p>
                      Technical and coding topics
                      identified by NLP.
                    </p>
                  </div>

                </div>

                <div className="analytics-summary-card">

                  <div className="summary-icon">
                    <Target size={20} />
                  </div>

                  <div>
                    <span>
                      Recruitment rounds
                    </span>

                    <strong>
                      {formatNumber(
                        totalRounds
                      )}
                    </strong>

                    <p>
                      Recruitment stages identified
                      from feedback.
                    </p>
                  </div>

                </div>

              </div>
            </section>

            {/* CONFIDENCE */}

            <section className="analytics-confidence-card">

              <div className="confidence-left">

                <div className="confidence-icon">
                  <Target size={22} />
                </div>

                <div>

                  <span className="confidence-label">
                    Data Confidence
                  </span>

                  <h2>
                    {averageConfidence.toFixed(2)}%
                  </h2>

                  <p>
                    Average confidence across the
                    analyzed placement intelligence
                    data.
                  </p>

                </div>

              </div>

              <div className="confidence-meter">

                <div className="confidence-meter-track">

                  <div
                    className="confidence-meter-fill"
                    style={{
                      width:
                        averageConfidence + "%",
                    }}
                  />

                </div>

                <div className="confidence-meter-labels">
                  <span>0%</span>
                  <span>100%</span>
                </div>

              </div>

            </section>

            {/* TOP INSIGHT */}

            {topTopic && (
              <section className="analytics-highlight">

                <div className="highlight-icon">
                  <TrendingUp size={22} />
                </div>

                <div>

                  <span>
                    Current Top Insight
                  </span>

                  <h3>
                    {topTopic.name} is currently
                    the most discussed topic.
                  </h3>

                  <p>
                    It appears in{" "}
                    {topTopic.count} analyzed
                    feedback discussions.
                  </p>

                </div>

              </section>
            )}

          </>
        )}
      </div>
    </main>
  );
}

export default Analytics;
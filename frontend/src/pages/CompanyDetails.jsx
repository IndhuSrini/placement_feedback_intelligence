import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
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
} from "lucide-react";

const API = "/api";

function formatDate(value) {
  if (!value) return "Not available";

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

function displayValue(value) {
  if (
    value === undefined ||
    value === null ||
    value === "" ||
    value === "null"
  ) {
    return "Not available";
  }

  return value;
}

/*
 * Display order for known companies.
 */
const COMPANY_ROUND_ORDER = {
  tcs: ["Coding", "Technical", "Aptitude", "HR"],

  infosys: ["Aptitude", "Coding", "Managerial", "HR"],

  "tech mahindra": [
    "Communication",
    "Aptitude",
    "Technical Programming",
    "HR",
  ],

  capgemini: [
    "Technical Programming",
    "Aptitude",
    "Communication",
    "Technical Interview",
    "HR",
  ],

  deloitte: [
    "Aptitude / Logical",
    "Case Study Discussion",
    "Technical Interview",
    "Managerial",
    "HR",
  ],

  hcltech: [
    "Coding",
    "Technical Interview",
    "Communication",
    "HR",
  ],

  accenture: [
    "Cognitive / Aptitude",
    "Technical Coding",
    "Communication",
    "Technical Interview",
    "HR",
  ],

  ibm: [
    "Technical Assessment",
    "Coding",
    "Group Discussion",
    "Technical Interview",
    "HR",
  ],

  freshworks: [
    "Programming Challenge",
    "Technical Discussion",
    "Problem Solving Interview",
    "HR",
  ],

  zoho: [
    "Basic Programming",
    "Advanced Programming",
    "Technical Interview",
    "HR",
  ],

  wipro: [
    "Communication",
    "Aptitude",
    "Coding",
    "Technical Interview",
    "HR",
  ],

  cognizant: [
    "Communication",
    "Technical Programming",
    "Aptitude",
    "Technical Interview",
    "HR",
  ],

  mistral: [
    "Technical Screening",
    "Coding",
    "System Design",
    "Managerial",
  ],

  "econ systems": [
    "Technical Coding",
    "Aptitude",
    "Technical Interview",
    "Communication",
    "HR",
  ],
};

/*
 * Converts database round names into common display names.
 */
function canonicalRoundName(round) {
  const type = String(round?.round_type || "").toLowerCase();
  const description = String(round?.description || "").toLowerCase();

  if (
    type.includes("managerial") ||
    description.includes("managerial")
  ) {
    return "Managerial";
  }

  if (
    type === "hr" ||
    type.includes("human resource") ||
    description === "hr" ||
    description.includes("hr interview")
  ) {
    return "HR";
  }

  if (
    type.includes("group discussion") ||
    description.includes("group discussion")
  ) {
    return "Group Discussion";
  }

  if (
    type.includes("case study") ||
    description.includes("case study")
  ) {
    return "Case Study Discussion";
  }

  if (
    type.includes("communication") ||
    description.includes("communication assessment")
  ) {
    return "Communication";
  }

  if (
    type.includes("aptitude") ||
    description.includes("aptitude")
  ) {
    return "Aptitude";
  }

  if (
    description.includes("system design") ||
    type.includes("system design")
  ) {
    return "System Design";
  }

  if (
    description.includes("technical screening") ||
    type.includes("technical screening")
  ) {
    return "Technical Screening";
  }

  if (
    description.includes("programming challenge") ||
    type.includes("programming challenge")
  ) {
    return "Programming Challenge";
  }

  if (
    description.includes("advanced programming") ||
    type.includes("advanced programming")
  ) {
    return "Advanced Programming";
  }

  if (
    description.includes("basic programming") ||
    type.includes("basic programming")
  ) {
    return "Basic Programming";
  }

  if (
    description.includes("technical programming") ||
    type.includes("technical programming")
  ) {
    return "Technical Programming";
  }

  if (
    description.includes("technical coding") ||
    type.includes("technical coding")
  ) {
    return "Technical Coding";
  }

  if (
    description.includes("technical assessment") ||
    type.includes("technical assessment")
  ) {
    return "Technical Assessment";
  }

  if (
    description.includes("technical discussion") ||
    type.includes("technical discussion")
  ) {
    return "Technical Discussion";
  }

  if (
    description.includes("problem solving interview") ||
    type.includes("problem solving interview")
  ) {
    return "Problem Solving Interview";
  }

  if (
    description.includes("technical interview") ||
    type.includes("technical interview")
  ) {
    return "Technical Interview";
  }

  if (
    type.includes("technical") ||
    description.includes("technical")
  ) {
    return "Technical";
  }

  if (
    type.includes("coding") ||
    description.includes("coding") ||
    description.includes("programming")
  ) {
    return "Coding";
  }

  return null;
}

/*
 * Builds clean recruitment rounds for display.
 */
function buildDisplayRounds(companyName, rawRounds) {
  const companyKey = String(companyName || "")
    .trim()
    .toLowerCase();

  const preferredOrder = COMPANY_ROUND_ORDER[companyKey];

  const detected = [];

  for (const round of rawRounds) {
    const canonical = canonicalRoundName(round);

    if (!canonical) continue;

    if (!detected.includes(canonical)) {
      detected.push(canonical);
    }
  }

  if (preferredOrder) {
    return preferredOrder.map((stage, index) => {
      const matching = rawRounds.filter(
        (round) => canonicalRoundName(round) === stage
      );

      const difficulty =
        matching.find((round) => round.difficulty)?.difficulty || "";

      return {
        id: `display-${companyKey}-${index}-${stage}`,
        round_number: index + 1,
        round_type: stage,
        description: stage,
        difficulty,
      };
    });
  }

  return detected.map((stage, index) => {
    const matching = rawRounds.find(
      (round) => canonicalRoundName(round) === stage
    );

    return {
      id: `display-${companyKey}-${index}-${stage}`,
      round_number: index + 1,
      round_type: stage,
      description: stage,
      difficulty: matching?.difficulty || "",
    };
  });
}

function CompanyDetails() {
  const { companyId } = useParams();
  const [searchParams] = useSearchParams();

  const [company, setCompany] = useState(null);
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  /*
   * Automatically opens the browser print dialog when
   * the page is opened using ?print=true.
   *
   * This is used by the Report button on Companies.jsx.
   */
  useEffect(() => {
    if (
      searchParams.get("print") === "true" &&
      !loading &&
      company
    ) {
      const timer = setTimeout(() => {
        window.print();
      }, 700);

      return () => clearTimeout(timer);
    }
  }, [searchParams, loading, company]);

  /*
   * Load company analytics and company information.
   */
  useEffect(() => {
    const loadCompanyDetails = async () => {
      try {
        setLoading(true);
        setError("");

        const detailsResponse = await fetch(
          `${API}/analytics/company/${companyId}`
        );

        if (!detailsResponse.ok) {
          throw new Error(
            `Failed to load company analytics: ${detailsResponse.status}`
          );
        }

        const detailsData = await detailsResponse.json();

        setDetails(detailsData);

        try {
          const companiesResponse = await fetch(
            `${API}/companies/`
          );

          if (companiesResponse.ok) {
            const companiesData =
              await companiesResponse.json();

            const selectedCompany =
              Array.isArray(companiesData)
                ? companiesData.find(
                    (item) =>
                      String(item.id) === String(companyId)
                  )
                : null;

            setCompany(selectedCompany);
          }
        } catch (companyError) {
          console.warn(
            "Could not load additional company information:",
            companyError
          );
        }
      } catch (err) {
        console.error("Company details error:", err);

        setError(
          err.message ||
            "Unable to load company details."
        );
      } finally {
        setLoading(false);
      }
    };

    loadCompanyDetails();
  }, [companyId]);

  /*
   * Manual report button.
   */
  const handleDownloadReport = () => {
    window.print();
  };

  if (loading) {
    return (
      <main className="company-details-page">
        <div className="company-details-container company-details-loading">
          <Loader2
            size={30}
            className="company-details-spin"
          />
          <p>Loading company details...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="company-details-page">
        <div className="company-details-container">

          <Link
            to="/companies"
            className="details-back-link"
          >
            <ArrowLeft size={16} />
            Back to Companies
          </Link>

          <section className="company-details-error">
            <CircleAlert size={32} />

            <h2>
              Unable to load company details
            </h2>

            <p>{error}</p>

            <Link
              to="/companies"
              className="details-primary-button"
            >
              Return to Companies
            </Link>
          </section>

        </div>
      </main>
    );
  }

  const data = details || {};

  const companyName =
    company?.name ||
    data.company ||
    "Company";

  const industry =
    company?.industry ||
    data.industry ||
    "Information Technology";

  const website =
    company?.website ||
    data.website ||
    null;

  const recruitmentDate =
    data.recruitment_date;

  const jobRole =
    data.job_role;

  const difficulty =
    data.difficulty;

  const eligibility =
    data.eligibility || {};

  const cgpa =
    eligibility.minimum_cgpa;

  const maximumBacklogs =
    eligibility.maximum_backlogs;

  const branchEligibility =
    eligibility.branch_eligibility;

  const otherCriteria =
    eligibility.other_criteria;

  const rawRounds =
    Array.isArray(data.rounds)
      ? data.rounds
      : [];

  const rounds =
    buildDisplayRounds(
      companyName,
      rawRounds
    );

  const roundsCount =
    rounds.length;

  const topics =
    Array.isArray(data.topics)
      ? data.topics
      : [];

  const questions =
    Array.isArray(data.frequent_questions)
      ? data.frequent_questions
      : [];

  return (
    <main className="company-details-page">
      <div className="company-details-container">

        {/* Top Actions */}

        <div className="company-details-actions">

          <Link
            to="/companies"
            className="details-back-link"
          >
            <ArrowLeft size={16} />
            Back to Companies
          </Link>

          <div className="company-details-action-buttons">

            <button
              type="button"
              className="details-report-button"
              onClick={handleDownloadReport}
            >
              <FileDown size={16} />
              Download Report
            </button>

            <button
              type="button"
              className="details-refresh-button"
              onClick={() => window.location.reload()}
            >
              <RefreshCw size={16} />
              Refresh
            </button>

          </div>
        </div>

        {/* Company Hero */}

        <section className="company-hero">

          <div className="company-hero-logo">
            {companyName
              .charAt(0)
              .toUpperCase()}
          </div>

          <div className="company-hero-content">

            <div className="details-eyebrow">
              <Building2 size={14} />
              Company Profile
            </div>

            <h1>{companyName}</h1>

            <div className="company-hero-meta">

              <span>
                <Building2 size={15} />
                {industry}
              </span>

              {website && (
                <a
                  href={website}
                  target="_blank"
                  rel="noreferrer"
                >
                  <ExternalLink size={14} />
                  Official Website
                </a>
              )}

            </div>

          </div>
        </section>

        {/* Statistics */}

        <section className="details-stats-grid">

          <article className="details-stat-card">
            <div className="details-stat-icon purple">
              <CalendarDays size={20} />
            </div>

            <div>
              <span>
                Recruitment Date
              </span>

              <strong>
                {formatDate(
                  recruitmentDate
                )}
              </strong>
            </div>
          </article>

          <article className="details-stat-card">
            <div className="details-stat-icon blue">
              <BriefcaseBusiness size={20} />
            </div>

            <div>
              <span>
                Job Role
              </span>

              <strong>
                {displayValue(jobRole)}
              </strong>
            </div>
          </article>

          <article className="details-stat-card">
            <div className="details-stat-icon green">
              <Layers3 size={20} />
            </div>

            <div>
              <span>
                Recruitment Rounds
              </span>

              <strong>
                {roundsCount ||
                  "Not available"}
              </strong>
            </div>
          </article>

          <article className="details-stat-card">
            <div className="details-stat-icon orange">
              <Target size={20} />
            </div>

            <div>
              <span>
                Difficulty
              </span>

              <strong>
                {displayValue(
                  difficulty
                )}
              </strong>
            </div>
          </article>

        </section>

        {/* Eligibility */}

        <section className="details-section">

          <div className="details-section-heading">

            <div className="details-section-icon">
              <GraduationCap size={19} />
            </div>

            <div>
              <h2>Eligibility</h2>

              <p>
                Requirements reported in placement feedback
              </p>
            </div>

          </div>

          <div className="eligibility-grid">

            <div className="eligibility-card">

              <span>
                Minimum CGPA
              </span>

              <strong>
                {displayValue(cgpa)}
              </strong>

            </div>

            <div className="eligibility-card">

              <span>
                Maximum Backlogs
              </span>

              <strong>
                {maximumBacklogs === 0
                  ? "No backlogs"
                  : displayValue(
                      maximumBacklogs
                    )}
              </strong>

            </div>

            <div className="eligibility-card">

              <span>
                Branch Eligibility
              </span>

              <strong>
                {displayValue(
                  branchEligibility
                )}
              </strong>

            </div>

            {otherCriteria && (
              <div className="eligibility-description">

                <CheckCircle2 size={17} />

                <span>
                  {otherCriteria}
                </span>

              </div>
            )}

          </div>
        </section>

        {/* Recruitment Rounds */}

        <section className="details-section">

          <div className="details-section-heading">

            <div className="details-section-icon">
              <Layers3 size={19} />
            </div>

            <div>
              <h2>
                Recruitment Rounds
              </h2>

              <p>
                Stages identified from placement feedback
              </p>
            </div>

          </div>

          {rounds.length > 0 ? (

            <div className="rounds-list">

              {rounds.map(
                (round, index) => (
                  <article
                    className="round-card"
                    key={
                      round.id ||
                      index
                    }
                  >

                    <div className="round-number">
                      {index + 1}
                    </div>

                    <div className="round-content">

                      <h3>
                        {round.round_type ||
                          "Recruitment Round"}
                      </h3>

                      <span>
                        {round.description ||
                          "Details available from placement feedback"}
                      </span>

                      {round.difficulty && (
                        <small>
                          Difficulty:{" "}
                          {round.difficulty}
                        </small>
                      )}

                    </div>

                  </article>
                )
              )}

            </div>

          ) : (

            <div className="details-empty">

              <Layers3 size={22} />

              <p>
                No recruitment round details
                available yet.
              </p>

            </div>

          )}

        </section>

        {/* Important Topics */}

        <section className="details-section">

          <div className="details-section-heading">

            <div className="details-section-icon">
              <Code2 size={19} />
            </div>

            <div>

              <h2>
                Important Topics
              </h2>

              <p>
                Technical and coding topics mentioned in feedback
              </p>

            </div>

          </div>

          {topics.length > 0 ? (

            <div className="topics-list">

              {topics.map(
                (topic, index) => (
                  <div
                    className="topic-chip"
                    key={
                      topic.id ||
                      `${topic.topic}-${index}`
                    }
                  >

                    <span>
                      {topic.topic ||
                        "Topic"}
                    </span>

                    <small>
                      {topic.category ||
                        "Technical"}
                    </small>

                  </div>
                )
              )}

            </div>

          ) : (

            <div className="details-empty">

              <Code2 size={22} />

              <p>
                No topic data available yet.
              </p>

            </div>

          )}

        </section>

        {/* Frequently Asked Questions */}

        <section className="details-section questions-section">

          <div className="details-section-heading">

            <div className="details-section-icon">
              <MessageSquareText size={19} />
            </div>

            <div>

              <h2>
                Frequently Asked Questions
              </h2>

              <p>
                Questions reported by students for this company
              </p>

            </div>

            <div className="questions-count">
              {questions.length} questions
            </div>

          </div>

          {questions.length > 0 ? (

            <div className="questions-list">

              {questions.map(
                (question, index) => (
                  <article
                    className="question-card"
                    key={
                      question.id ||
                      index
                    }
                  >

                    <div className="question-number">
                      {index + 1}
                    </div>

                    <div className="question-content">

                      <h3>
                        {String(
                          question.question ||
                          question.question_text ||
                          "Question"
                        ).replace(
                          /\*\*/g,
                          ""
                        )}
                      </h3>

                      <div className="question-meta">

                        <span>
                          Asked{" "}
                          {question.occurrence_count ||
                            1}{" "}
                          time
                          {(question.occurrence_count ||
                            1) === 1
                            ? ""
                            : "s"}
                        </span>

                        {question.difficulty && (
                          <span>
                            {question.difficulty}
                          </span>
                        )}

                        {question.verification_status && (
                          <span>
                            {
                              question.verification_status
                            }
                          </span>
                        )}

                      </div>

                    </div>

                  </article>
                )
              )}

            </div>

          ) : (

            <div className="details-empty">

              <MessageSquareText size={22} />

              <p>
                No frequently asked questions are available
                for this company yet.
              </p>

            </div>

          )}

        </section>

        {/* Footer */}

        <section className="company-details-footer">

          <Users size={18} />

          <span>
            Details are generated from placement feedback
            collected by the system.
          </span>

        </section>

      </div>
    </main>
  );
}

export default CompanyDetails;
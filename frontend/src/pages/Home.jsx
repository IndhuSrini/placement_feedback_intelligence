import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  Brain,
  Building2,
  Code2,
  Database,
  GraduationCap,
  Layers3,
  Loader2,
  MessageSquare,
  MessageSquareText,
  Send,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Trophy,
  Cpu,
  FileCheck2,
} from "lucide-react";

const API = "/api";

export default function Home() {
  const [overview, setOverview] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);

  const token = localStorage.getItem("admin_token");

  // Fetch real backend data
  useEffect(() => {
    async function fetchStats() {
      try {
        setLoadingStats(true);

        const overviewRes = await fetch(`${API}/analytics/overview`);
        if (overviewRes.ok) {
          const data = await overviewRes.json();
          setOverview(data);
        }
      } catch (err) {
        console.warn("Could not load home overview statistics:", err);
      } finally {
        setLoadingStats(false);
      }
    }

    fetchStats();
  }, []);

  const totalCompanies = overview?.total_companies ?? 18;
  const totalDrives = overview?.total_placement_drives ?? 15;
  const totalQuestions = overview?.total_questions ?? 135;
  const totalTopics = overview?.total_topics ?? 38;
  const totalRounds = overview?.total_recruitment_rounds ?? 126;

  return (
    <main className="home-page-compact">
      <div className="home-centered-container">
        {/* 1. COMPACT HERO SECTION */}
        <section className="home-hero-compact">
          <div className="home-hero-badge">
            <Sparkles size={14} />
            <span>AI-Powered Placement Intelligence</span>
          </div>

          <h1 className="home-hero-title">
            Placement Feedback <span className="gradient-highlight">Intelligence System</span>
          </h1>

          <p className="home-hero-lead">
            Converting unstructured candidate feedback into structured recruitment intelligence — covering companies, eligibility criteria, interview rounds, technical topics, questions, and difficulty analysis.
          </p>

          <div className="home-hero-actions">
            <Link to={token ? "/analytics" : "/login"} className="hero-btn-primary">
              <span>Explore Analytics</span>
              <ArrowRight size={16} />
            </Link>

            <Link to={token ? "/companies" : "/login"} className="hero-btn-secondary">
              <Building2 size={16} />
              <span>Explore Companies</span>
            </Link>
          </div>

          <div className="home-hero-trust-bar">
            <div className="trust-chip">
              <ShieldCheck size={14} className="text-indigo" />
              <span>2023–2027 CSE Batch Scope</span>
            </div>
            <span className="trust-dot">•</span>
            <div className="trust-chip">
              <Brain size={14} className="text-indigo" />
              <span>NLP Information Extraction</span>
            </div>
            <span className="trust-dot">•</span>
            <div className="trust-chip">
              <Database size={14} className="text-indigo" />
              <span>PostgreSQL Relational Storage</span>
            </div>
          </div>
        </section>

        {/* 2. COMPACT LIVE STATISTICS STRIP */}
        <section className="home-stats-compact">
          <div className="stats-strip-header">
            <span className="section-eyebrow">LIVE DATABASE METRICS</span>
            <h2>Synthesized from Placement Feedback</h2>
          </div>

          <div className="compact-stats-grid">
            <div className="compact-stat-card">
              <div className="stat-icon purple">
                <Building2 size={20} />
              </div>
              <div className="stat-info">
                <strong>{loadingStats ? <Loader2 size={20} className="spin-icon" /> : totalCompanies}</strong>
                <span>Recruiting Companies</span>
              </div>
            </div>

            <div className="compact-stat-card">
              <div className="stat-icon blue">
                <Trophy size={20} />
              </div>
              <div className="stat-info">
                <strong>{loadingStats ? <Loader2 size={20} className="spin-icon" /> : totalDrives}</strong>
                <span>Placement Drives</span>
              </div>
            </div>

            <div className="compact-stat-card">
              <div className="stat-icon teal">
                <MessageSquareText size={20} />
              </div>
              <div className="stat-info">
                <strong>{loadingStats ? <Loader2 size={20} className="spin-icon" /> : totalQuestions}</strong>
                <span>Questions Extracted</span>
              </div>
            </div>

            <div className="compact-stat-card">
              <div className="stat-icon orange">
                <Code2 size={20} />
              </div>
              <div className="stat-info">
                <strong>{loadingStats ? <Loader2 size={20} className="spin-icon" /> : totalTopics}</strong>
                <span>Technical Topics</span>
              </div>
            </div>

            <div className="compact-stat-card">
              <div className="stat-icon indigo">
                <Layers3 size={20} />
              </div>
              <div className="stat-info">
                <strong>{loadingStats ? <Loader2 size={20} className="spin-icon" /> : totalRounds}</strong>
                <span>Recruitment Rounds</span>
              </div>
            </div>
          </div>
        </section>

        {/* 3. COMPACT SYSTEM PIPELINE FLOW */}
        <section className="home-pipeline-compact">
          <div className="section-heading text-center">
            <span className="section-eyebrow">SYSTEM WORKFLOW</span>
            <h2>From Unstructured Feedback to Intelligence</h2>
          </div>

          <div className="compact-pipeline-flow">
            <div className="pipeline-compact-step">
              <span className="step-num">01</span>
              <MessageSquare size={16} />
              <strong>Feedback</strong>
              <small>Student Reports</small>
            </div>
            <div className="pipeline-arrow">→</div>

            <div className="pipeline-compact-step">
              <span className="step-num">02</span>
              <Send size={16} />
              <strong>Telegram</strong>
              <small>Telethon Client</small>
            </div>
            <div className="pipeline-arrow">→</div>

            <div className="pipeline-compact-step">
              <span className="step-num">03</span>
              <Cpu size={16} />
              <strong>NLP Engine</strong>
              <small>Regex & Parser</small>
            </div>
            <div className="pipeline-arrow">→</div>

            <div className="pipeline-compact-step">
              <span className="step-num">04</span>
              <FileCheck2 size={16} />
              <strong>Extraction</strong>
              <small>Entity Parsing</small>
            </div>
            <div className="pipeline-arrow">→</div>

            <div className="pipeline-compact-step">
              <span className="step-num">05</span>
              <Database size={16} />
              <strong>PostgreSQL</strong>
              <small>Relational DB</small>
            </div>
            <div className="pipeline-arrow">→</div>

            <div className="pipeline-compact-step highlight">
              <span className="step-num">06</span>
              <BarChart3 size={16} />
              <strong>Intelligence</strong>
              <small>Analytics Dashboard</small>
            </div>
          </div>
        </section>

        {/* 4. COMPACT NLP CAPABILITIES CHIPS */}
        <section className="home-nlp-chips-section">
          <div className="section-heading text-center">
            <span className="section-eyebrow">CORE NLP CAPABILITIES</span>
            <h2>Automated Entity & Pattern Recognition</h2>
          </div>

          <div className="nlp-chips-grid">
            <div className="nlp-chip">
              <Building2 size={15} className="text-purple" />
              <span>Company Alias Extraction</span>
            </div>
            <div className="nlp-chip">
              <GraduationCap size={15} className="text-blue" />
              <span>CGPA Threshold Parsing</span>
            </div>
            <div className="nlp-chip">
              <ShieldCheck size={15} className="text-orange" />
              <span>Backlog Policy Detection</span>
            </div>
            <div className="nlp-chip">
              <Layers3 size={15} className="text-teal" />
              <span>Round Stage Classification</span>
            </div>
            <div className="nlp-chip">
              <TrendingUp size={15} className="text-indigo" />
              <span>Sequential Round Ordering</span>
            </div>
            <div className="nlp-chip">
              <Code2 size={15} className="text-purple" />
              <span>Technical Topic Mapping</span>
            </div>
            <div className="nlp-chip">
              <MessageSquareText size={15} className="text-blue" />
              <span>Question Pattern Extraction</span>
            </div>
            <div className="nlp-chip">
              <FileCheck2 size={15} className="text-green" />
              <span>Syntactic Question Deduplication</span>
            </div>
            <div className="nlp-chip">
              <Trophy size={15} className="text-orange" />
              <span>Drive Difficulty Classification</span>
            </div>
            <div className="nlp-chip">
              <Sparkles size={15} className="text-indigo" />
              <span>Reliability Confidence Scoring</span>
            </div>
            <div className="nlp-chip">
              <Brain size={15} className="text-teal" />
              <span>Feedback Category Categorization</span>
            </div>
            <div className="nlp-chip">
              <Database size={15} className="text-purple" />
              <span>Normalized Database Indexing</span>
            </div>
          </div>
        </section>

        {/* 5. DIRECT ACCESS CARDS */}
        <section className="home-quick-access-compact">
          <div className="quick-grid">
            <div className="quick-card">
              <div className="quick-icon-box purple">
                <BarChart3 size={20} />
              </div>
              <div>
                <h3>Analytics Dashboard</h3>
                <p>Inspect topic frequencies, difficulty distributions, category charts, and recruitment metrics.</p>
              </div>
              <Link to={token ? "/analytics" : "/login"} className="quick-link">
                <span>View Analytics</span>
                <ArrowRight size={14} />
              </Link>
            </div>

            <div className="quick-card">
              <div className="quick-icon-box blue">
                <Building2 size={20} />
              </div>
              <div>
                <h3>Company Directory</h3>
                <p>Browse {totalCompanies} tracked companies, view recruitment stages, interview questions, and reports.</p>
              </div>
              <Link to={token ? "/companies" : "/login"} className="quick-link">
                <span>Browse Companies</span>
                <ArrowRight size={14} />
              </Link>
            </div>

            <div className="quick-card">
              <div className="quick-icon-box teal">
                <Brain size={20} />
              </div>
              <div>
                <h3>System Architecture</h3>
                <p>Review the technical NLP pipeline, PostgreSQL database schemas, and engineering capstone documentation.</p>
              </div>
              <Link to="/about" className="quick-link">
                <span>Documentation</span>
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
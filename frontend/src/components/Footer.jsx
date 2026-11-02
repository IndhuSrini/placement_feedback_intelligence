import { Link } from "react-router-dom";
import {
  BarChart3,
  ShieldCheck,
  Building2,
  Brain,
  Layers3,
  Code2,
} from "lucide-react";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-container">
        {/* Top Grid */}
        <div className="footer-grid">
          {/* Column 1: Brand & Overview */}
          <div className="footer-brand-col">
            <Link to="/" className="footer-brand">
              <div className="footer-brand-icon">
                <BarChart3 size={20} strokeWidth={2.4} />
              </div>
              <div>
                <span className="footer-brand-title">Placement Intelligence</span>
                <span className="footer-brand-tag">Feedback Analytics</span>
              </div>
            </Link>

            <p className="footer-description">
              An AI-assisted placement intelligence platform transforming
              unstructured student placement feedback into structured recruitment
              knowledge, interview questions, technical topics, and actionable
              dashboards.
            </p>

            <div className="footer-batch-pill">
              <ShieldCheck size={14} />
              <span>B.E. CSE • 2023–2027 Batch Cycle</span>
            </div>
          </div>

          {/* Column 2: Navigation Links */}
          <div className="footer-links-col">
            <h4>Platform</h4>
            <ul>
              <li>
                <Link to="/">Home Overview</Link>
              </li>
              <li>
                <Link to="/analytics">Analytics Dashboard</Link>
              </li>
              <li>
                <Link to="/companies">Companies Directory</Link>
              </li>
              <li>
                <Link to="/about">System Architecture</Link>
              </li>
              <li>
                <Link to="/login">Admin Access</Link>
              </li>
            </ul>
          </div>

          {/* Column 3: Core NLP Stages */}
          <div className="footer-links-col">
            <h4>Intelligence Pipeline</h4>
            <ul>
              <li>
                <span className="footer-static-item">
                  <Brain size={14} /> Information Extraction
                </span>
              </li>
              <li>
                <span className="footer-static-item">
                  <Layers3 size={14} /> Recruitment Round Stages
                </span>
              </li>
              <li>
                <span className="footer-static-item">
                  <Code2 size={14} /> Question Deduplication
                </span>
              </li>
              <li>
                <span className="footer-static-item">
                  <Building2 size={14} /> Company Intelligence
                </span>
              </li>
              <li>
                <span className="footer-static-item">
                  <ShieldCheck size={14} /> Confidence Scoring
                </span>
              </li>
            </ul>
          </div>

          {/* Column 4: Project Info */}
          <div className="footer-links-col">
            <h4>Technology & Context</h4>
            <p className="footer-tech-summary">
              Powered by Python FastAPI, PostgreSQL, Telethon Ingestion,
              Rule-based NLP & Classification, and React + Vite with Recharts.
            </p>
            <div className="footer-tech-tags">
              <span>FastAPI</span>
              <span>PostgreSQL</span>
              <span>NLP</span>
              <span>React 19</span>
              <span>Recharts</span>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="footer-bottom">
          <div className="footer-bottom-left">
            <span>© {new Date().getFullYear()} Placement Feedback Intelligence. Final Year CSE Engineering Project.</span>
          </div>

          <div className="footer-bottom-right">
            <span className="footer-status-indicator">
              <span className="footer-status-dot" />
              <span>System Active & Verified</span>
            </span>
            <Link to="/about" className="footer-bottom-link">
              Documentation
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

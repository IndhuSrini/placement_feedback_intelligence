import {
  ArrowRight,
  BarChart3,
  Brain,
  Database,
  MessageSquareText,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import { Link } from "react-router-dom";

function Home() {
  return (
    <main>
      {/* Hero */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="status-dot"></span>
            AI-powered placement intelligence
          </div>

          <h1>
            Turn Placement Feedback
            <span> Into Intelligence.</span>
          </h1>

          <p className="hero-description">
            PlacementIQ transforms authorized placement-group feedback into
            structured insights about companies, eligibility, recruitment
            rounds, interview questions, topics and difficulty.
          </p>

          <div className="hero-actions">
            <Link to="/analytics" className="primary-button">
              Explore Analytics
              <ArrowRight size={18} />
            </Link>

            <Link to="/about" className="secondary-button">
              Learn More
            </Link>
          </div>

          <div className="hero-trust">
            <ShieldCheck size={17} />
            Built for the 2023–2027 placement cycle
          </div>
        </div>

        <div className="hero-visual">
          <div className="dashboard-preview">
            <div className="preview-header">
              <div>
                <span className="preview-label">PLACEMENT OVERVIEW</span>
                <h3>Recruitment Intelligence</h3>
              </div>

              <div className="preview-icon">
                <TrendingUp size={20} />
              </div>
            </div>

            <div className="preview-stats">
              <div>
                <strong>17</strong>
                <span>Companies</span>
              </div>

              <div>
                <strong>78</strong>
                <span>Questions</span>
              </div>

              <div>
                <strong>24</strong>
                <span>Topics</span>
              </div>
            </div>

            <div className="mini-chart">
              <div className="chart-bars">
                <span style={{ height: "42%" }}></span>
                <span style={{ height: "65%" }}></span>
                <span style={{ height: "50%" }}></span>
                <span style={{ height: "82%" }}></span>
                <span style={{ height: "70%" }}></span>
                <span style={{ height: "94%" }}></span>
                <span style={{ height: "78%" }}></span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="stats-section">
        <div className="section-container">
          <div className="stat-grid">
            <div className="stat-box">
              <div className="stat-icon">
                <Database size={21} />
              </div>
              <strong>17</strong>
              <span>Companies tracked</span>
            </div>

            <div className="stat-box">
              <div className="stat-icon">
                <BarChart3 size={21} />
              </div>
              <strong>5</strong>
              <span>Placement drives</span>
            </div>

            <div className="stat-box">
              <div className="stat-icon">
                <MessageSquareText size={21} />
              </div>
              <strong>78</strong>
              <span>Questions analyzed</span>
            </div>

            <div className="stat-box">
              <div className="stat-icon">
                <Brain size={21} />
              </div>
              <strong>24</strong>
              <span>Topics identified</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <div className="section-container">
          <div className="section-heading">
            <span>WHAT PLACEMENTIQ DOES</span>
            <h2>From raw feedback to useful insights</h2>
            <p>
              The system organizes placement discussions into information
              students and placement coordinators can actually use.
            </p>
          </div>

          <div className="feature-grid">
            <FeatureCard
              icon={<MessageSquareText />}
              title="Feedback Intelligence"
              description="Processes placement feedback and identifies useful recruitment information from student messages."
            />

            <FeatureCard
              icon={<Brain />}
              title="NLP Extraction"
              description="Extracts eligibility, rounds, interview questions, topics and difficulty from unstructured feedback."
            />

            <FeatureCard
              icon={<BarChart3 />}
              title="Analytics Dashboard"
              description="Visualizes recruitment trends, frequently discussed topics and interview question patterns."
            />

            <FeatureCard
              icon={<Database />}
              title="Structured Knowledge"
              description="Stores processed placement intelligence in PostgreSQL for consistent access and analysis."
            />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="cta-box">
          <div>
            <span className="cta-label">PLACEMENT INTELLIGENCE</span>
            <h2>Explore what the feedback reveals.</h2>
            <p>
              Browse recruitment analytics and discover patterns across
              placement drives.
            </p>
          </div>

          <Link to="/analytics" className="primary-button">
            Open Dashboard
            <ArrowRight size={18} />
          </Link>
        </div>
      </section>
    </main>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="feature-card">
      <div className="feature-icon">{icon}</div>

      <h3>{title}</h3>

      <p>{description}</p>

      <div className="feature-arrow">
        <ArrowRight size={16} />
      </div>
    </div>
  );
}

export default Home;
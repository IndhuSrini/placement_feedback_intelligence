import { BookOpenText, BrainCircuit, Database, Rocket, Sparkles } from 'lucide-react'

const About = () => (
  <div className="page-shell container about-page">
    <div className="about-layout">
      <div>
        <p className="section-kicker">About the project</p>
        <h1>What is Placement Feedback Intelligence?</h1>
        <p className="page-intro">
          Placement feedback is often scattered across Telegram messages, student conversations, and interview chatter. It is difficult to organize manually and even harder to turn into actionable recruitment intelligence.
        </p>
        <p className="page-intro">
          This project transforms unstructured placement feedback into a structured and searchable intelligence system for students, colleges, and placement teams.
        </p>
      </div>

      <div className="about-visual">
        <div className="about-visual-card" aria-label="Product intelligence illustration">
          <div className="visual-pill">AI-assisted placement analytics</div>
          <div className="mini-stack">
            <div className="mini-row">
              <span className="mini-label">Companies</span>
              <strong>18</strong>
            </div>
            <div className="mini-row">
              <span className="mini-label">Questions</span>
              <strong>350+</strong>
            </div>
            <div className="mini-row highlight-row">
              <span className="mini-label">Insights</span>
              <strong>92%</strong>
            </div>
          </div>
          <div className="visual-sparkline" aria-hidden="true">
            <span style={{ height: '18%' }} />
            <span style={{ height: '32%' }} />
            <span style={{ height: '28%' }} />
            <span style={{ height: '58%' }} />
            <span style={{ height: '72%' }} />
            <span style={{ height: '65%' }} />
            <span style={{ height: '88%' }} />
          </div>
        </div>
      </div>
    </div>

    <section className="content-panel full-width-panel">
      <div className="panel-header-row"><h3>The problem</h3></div>
      <p className="content-copy">
        Placement feedback is usually fragmented, repetitive, and hard to compare across companies and interview rounds. Without a structured view, it becomes difficult to see common patterns in questions, requirements, and company-specific preparation priorities.
      </p>
    </section>

    <section className="content-panel full-width-panel">
      <div className="panel-header-row"><h3>Our solution</h3></div>
      <p className="content-copy">
        The system collects placement-related messages, processes them through an NLP pipeline, extracts topics and questions, filters duplicates, stores the data in PostgreSQL, and transforms the results into company-level analytics and insight summaries.
      </p>
    </section>

    <section className="content-panel full-width-panel">
      <div className="panel-header-row"><h3>How it works</h3></div>
      <div className="process-flow compact-flow">
        <div className="process-step"><div className="process-node"><Database size={18} /></div><span>Telegram</span></div>
        <div className="process-step"><div className="process-node"><BookOpenText size={18} /></div><span>Collection</span></div>
        <div className="process-step"><div className="process-node"><BrainCircuit size={18} /></div><span>NLP</span></div>
        <div className="process-step"><div className="process-node"><Sparkles size={18} /></div><span>Extraction</span></div>
        <div className="process-step"><div className="process-node"><Rocket size={18} /></div><span>Analytics</span></div>
      </div>
    </section>

    <section className="content-panel full-width-panel">
      <div className="panel-header-row"><h3>Technology stack</h3></div>
      <div className="insights-grid compact-grid">
        <div className="insight-card">
          <h4>Frontend</h4>
          <p>React, Vite, Axios, Recharts</p>
        </div>
        <div className="insight-card">
          <h4>Backend</h4>
          <p>FastAPI, Python</p>
        </div>
        <div className="insight-card">
          <h4>Database</h4>
          <p>PostgreSQL</p>
        </div>
        <div className="insight-card">
          <h4>NLP</h4>
          <p>Python NLP pipeline</p>
        </div>
      </div>
    </section>

    <section className="content-panel full-width-panel">
      <div className="panel-header-row"><h3>Project scope</h3></div>
      <p className="content-copy">This project focuses on the 2023–27 batch and is designed as a prototype for placement intelligence and institutional analytics.</p>
    </section>

    <section className="content-panel full-width-panel highlight-note">
      <div className="panel-header-row"><h3>Data notice</h3></div>
      <p className="content-copy">
        This prototype uses synthetic placement feedback for development and demonstration purposes. The data shown should not be interpreted as actual placement outcomes.
      </p>
    </section>
  </div>
)

export default About

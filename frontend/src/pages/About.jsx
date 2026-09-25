import {
  Brain,
  Database,
  MessageSquareText,
  Server,
  ShieldCheck,
} from "lucide-react";

function About() {
  return (
    <main className="page-container">
      <section className="inner-hero">
        <div className="hero-badge">
          <Brain size={16} />
          About PlacementIQ
        </div>

        <h1>
          Making placement feedback
          <span> more useful.</span>
        </h1>

        <p>
          Placement Feedback Intelligence is an AI-assisted system designed to
          transform unstructured placement feedback into structured,
          searchable and meaningful placement intelligence.
        </p>
      </section>

      <section className="about-grid">
        <div className="about-card">
          <div className="feature-icon">
            <MessageSquareText />
          </div>

          <h2>Problem</h2>

          <p>
            Placement information is often scattered across student
            conversations. Important details such as eligibility, recruitment
            rounds and interview questions can be difficult to find later.
          </p>
        </div>

        <div className="about-card">
          <div className="feature-icon">
            <Brain />
          </div>

          <h2>Solution</h2>

          <p>
            PlacementIQ processes authorized feedback, extracts important
            information using NLP techniques and stores the resulting
            knowledge in a structured database.
          </p>
        </div>
      </section>

      <section className="workflow-section">
        <div className="section-heading">
          <span>SYSTEM WORKFLOW</span>
          <h2>From message to insight</h2>
        </div>

        <div className="workflow-grid">
          <Workflow
            icon={<MessageSquareText />}
            number="01"
            title="Collect"
            text="Authorized placement feedback is collected from the configured source."
          />

          <Workflow
            icon={<Brain />}
            number="02"
            title="Analyze"
            text="NLP identifies recruitment information, topics, questions and difficulty."
          />

          <Workflow
            icon={<Database />}
            number="03"
            title="Store"
            text="Extracted information is organized and stored in PostgreSQL."
          />

          <Workflow
            icon={<Server />}
            number="04"
            title="Visualize"
            text="FastAPI provides analytics that are displayed through the dashboard."
          />
        </div>
      </section>

      <section className="technology-section">
        <div className="section-heading">
          <span>TECHNOLOGY</span>
          <h2>Built with a practical architecture</h2>
        </div>

        <div className="tech-list">
          <Tech name="React + Vite" />
          <Tech name="FastAPI" />
          <Tech name="Python NLP" />
          <Tech name="PostgreSQL" />
          <Tech name="REST APIs" />
          <Tech name="Authorized Telegram ingestion" />
        </div>
      </section>

      <div className="about-note">
        <ShieldCheck size={20} />
        <div>
          <strong>Designed around authorized placement feedback</strong>
          <p>
            The system is intended to work with placement information that the
            project is authorized to collect and process.
          </p>
        </div>
      </div>
    </main>
  );
}

function Workflow({ icon, number, title, text }) {
  return (
    <div className="workflow-card">
      <div className="workflow-top">
        <div className="feature-icon">{icon}</div>
        <span>{number}</span>
      </div>

      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  );
}

function Tech({ name }) {
  return (
    <div className="tech-pill">
      <span></span>
      {name}
    </div>
  );
}

export default About;
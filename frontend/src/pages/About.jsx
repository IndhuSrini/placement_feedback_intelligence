import {
  Brain,
  Database,
  MessageSquareText,
  Server,
  ShieldCheck,
  Building2,
  Layers3,
  Code2,
  Target,
  GraduationCap,
  Users,
  Cpu,
  Send,
  FileCheck2,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

export default function About() {
  return (
    <main className="about-page-wrapper">
      <div className="about-container">
        {/* HERO SECTION */}
        <section className="about-hero">
          <div className="about-hero-badge">
            <Sparkles size={14} />
            <span>Project Documentation & System Architecture</span>
          </div>

          <h1>
            Placement Feedback <span className="gradient-text">Intelligence System</span>
          </h1>

          <p className="about-hero-lead">
            An AI-assisted placement intelligence platform engineered to transform unstructured candidate interview feedback into structured, actionable recruitment insights for students, faculty mentors, and placement officers.
          </p>
        </section>

        {/* 1. PROJECT OVERVIEW */}
        <section className="about-section">
          <div className="about-section-header">
            <div className="about-icon-box purple">
              <Brain size={22} />
            </div>
            <div>
              <h2>1. Project Overview</h2>
              <p>Core mission and architectural vision</p>
            </div>
          </div>
          <div className="about-card-body">
            <p>
              During campus recruitment cycles, hundreds of engineering students participate in drive assessments, coding evaluations, and technical interviews. While candidates share valuable feedback regarding questions, topics, cutoffs, and round structures in informal channels, this information remains unstructured, chaotic, and transient.
            </p>
            <p>
              <strong>Placement Feedback Intelligence</strong> automates the harvesting, NLP parsing, normalization, relational indexing, and visual reporting of placement data, converting candidate feedback into structured institutional memory.
            </p>
          </div>
        </section>

        {/* 2. PROBLEM STATEMENT */}
        <section className="about-section">
          <div className="about-section-header">
            <div className="about-icon-box orange">
              <Target size={22} />
            </div>
            <div>
              <h2>2. Problem Statement</h2>
              <p>Challenges in traditional placement feedback management</p>
            </div>
          </div>
          <div className="about-grid-3">
            <div className="about-subcard">
              <MessageSquareText className="text-orange" size={20} />
              <h3>Scattered Feedback</h3>
              <p>
                Student interview experiences remain buried in instant messaging feeds, chat channels, and offline notes, rendering historical retrieval nearly impossible.
              </p>
            </div>
            <div className="about-subcard">
              <Layers3 className="text-orange" size={20} />
              <h3>Unstructured Format</h3>
              <p>
                Raw feedback lacks uniform structure — mixing eligibility criteria, round order, technical questions, and difficulty ratings in noisy prose.
              </p>
            </div>
            <div className="about-subcard">
              <Users className="text-orange" size={20} />
              <h3>Redundant Preparation</h3>
              <p>
                Junior batches repeatedly ask the same questions prior to company drives due to lack of an organized, searchable question bank and company profile directory.
              </p>
            </div>
          </div>
        </section>

        {/* 3. PROJECT OBJECTIVES */}
        <section className="about-section">
          <div className="about-section-header">
            <div className="about-icon-box blue">
              <CheckCircle2 size={22} />
            </div>
            <div>
              <h2>3. Project Objectives</h2>
              <p>Primary capabilities and functional goals</p>
            </div>
          </div>
          <div className="about-grid-2">
            <div className="about-feature-item">
              <FileCheck2 size={18} className="text-blue" />
              <div>
                <strong>Structured Information Extraction:</strong> Automatically parse raw natural text into clean entity attributes (CGPA, backlogs, topics, rounds).
              </div>
            </div>
            <div className="about-feature-item">
              <Brain size={18} className="text-blue" />
              <div>
                <strong>NLP-Based Linguistic Analysis:</strong> Apply regex tokenization and custom keyword aliasing to standardize technical domain terms.
              </div>
            </div>
            <div className="about-feature-item">
              <Building2 size={18} className="text-blue" />
              <div>
                <strong>Company Intelligence Profiles:</strong> Aggregating company-specific interview records, eligibility cutoffs, and overall drive difficulty.
              </div>
            </div>
            <div className="about-feature-item">
              <Layers3 size={18} className="text-blue" />
              <div>
                <strong>Recruitment-Round Analysis:</strong> Classifying and ordering drive stages from initial cognitive screening to technical and HR rounds.
              </div>
            </div>
            <div className="about-feature-item">
              <Code2 size={18} className="text-blue" />
              <div>
                <strong>Question Intelligence & Deduplication:</strong> Cataloguing real questions with fuzzy deduplication and occurrence frequency tracking.
              </div>
            </div>
            <div className="about-feature-item">
              <ShieldCheck size={18} className="text-blue" />
              <div>
                <strong>Eligibility & Reliability Verification:</strong> Normalizing candidate-reported CGPA and backlog criteria with AI confidence scoring.
              </div>
            </div>
          </div>
        </section>

        {/* 4. HOW THE SYSTEM WORKS (PIPELINE) */}
        <section className="about-section">
          <div className="about-section-header">
            <div className="about-icon-box teal">
              <Cpu size={22} />
            </div>
            <div>
              <h2>4. How the System Works</h2>
              <p>End-to-end data processing workflow</p>
            </div>
          </div>
          <div className="about-pipeline-flow">
            <div className="about-pipeline-step">
              <span className="step-num">01</span>
              <MessageSquareText size={18} />
              <strong>Placement Feedback</strong>
              <small>Student Submissions</small>
            </div>
            <div className="flow-arrow">→</div>
            <div className="about-pipeline-step">
              <span className="step-num">02</span>
              <Send size={18} />
              <strong>Telegram Ingestion</strong>
              <small>Telethon Client</small>
            </div>
            <div className="flow-arrow">→</div>
            <div className="about-pipeline-step">
              <span className="step-num">03</span>
              <Cpu size={18} />
              <strong>NLP Processing</strong>
              <small>Regex & Aliasing</small>
            </div>
            <div className="flow-arrow">→</div>
            <div className="about-pipeline-step">
              <span className="step-num">04</span>
              <FileCheck2 size={18} />
              <strong>Information Extraction</strong>
              <small>Entity Parsing</small>
            </div>
            <div className="flow-arrow">→</div>
            <div className="about-pipeline-step">
              <span className="step-num">05</span>
              <Database size={18} />
              <strong>PostgreSQL Storage</strong>
              <small>Relational Schema</small>
            </div>
            <div className="flow-arrow">→</div>
            <div className="about-pipeline-step">
              <span className="step-num">06</span>
              <Server size={18} />
              <strong>Analytics API</strong>
              <small>FastAPI Backend</small>
            </div>
            <div className="flow-arrow">→</div>
            <div className="about-pipeline-step highlighted">
              <span className="step-num">07</span>
              <Sparkles size={18} />
              <strong>Placement Intelligence</strong>
              <small>React UI Portal</small>
            </div>
          </div>
        </section>

        {/* 5. NLP CAPABILITIES */}
        <section className="about-section">
          <div className="about-section-header">
            <div className="about-icon-box indigo">
              <Brain size={22} />
            </div>
            <div>
              <h2>5. Core NLP Capabilities</h2>
              <p>Specialized linguistic rules and extraction models</p>
            </div>
          </div>
          <div className="about-grid-3">
            <div className="nlp-cap-card">
              <h4>Company & Role Identification</h4>
              <p>Alias resolution maps variations (e.g. TCS ASE, TCS Digital, Infosys DSE) to standardized canonical company records.</p>
            </div>
            <div className="nlp-cap-card">
              <h4>CGPA & Backlog Extraction</h4>
              <p>Regex numerical extraction identifies decimal CGPA cutoffs (6.5, 7.0, 7.5) and backlog policies ("0 backlogs", "max 1 history").</p>
            </div>
            <div className="nlp-cap-card">
              <h4>Recruitment Round Ordering</h4>
              <p>Rule-based classifier identifies drive stages (Aptitude, Coding, Technical 1, Technical 2, HR) in sequential order.</p>
            </div>
            <div className="nlp-cap-card">
              <h4>Technical Topic Classification</h4>
              <p>Maps keywords across DBMS, OOP, Operating Systems, Computer Networks, and DSA to standardized topic tags.</p>
            </div>
            <div className="nlp-cap-card">
              <h4>Question Extraction & Deduplication</h4>
              <p>Extracts interview questions and merges syntactic duplicates while updating candidate occurrence counts.</p>
            </div>
            <div className="nlp-cap-card">
              <h4>Difficulty & Confidence Scoring</h4>
              <p>Calculates item completeness confidence ratings (0–100%) and overall drive difficulty levels (Easy, Medium, Hard).</p>
            </div>
          </div>
        </section>

        {/* 6. ANALYTICS & INTELLIGENCE */}
        <section className="about-section">
          <div className="about-section-header">
            <div className="about-icon-box violet">
              <Server size={22} />
            </div>
            <div>
              <h2>6. Analytics & Intelligence Capabilities</h2>
              <p>Data visualization and decision support features</p>
            </div>
          </div>
          <div className="about-grid-2">
            <div className="about-bullet-box">
              <Code2 size={16} className="text-purple" />
              <div>
                <strong>Topic Frequency Intelligence:</strong> Recharts-powered horizontal bar charts displaying high-frequency subject areas tested across companies.
              </div>
            </div>
            <div className="about-bullet-box">
              <MessageSquareText size={16} className="text-purple" />
              <div>
                <strong>Question Bank Intelligence:</strong> Categorized question bank sorted by frequency of occurrence with difficulty tags and confidence metrics.
              </div>
            </div>
            <div className="about-bullet-box">
              <Building2 size={16} className="text-purple" />
              <div>
                <strong>Company Intelligence Dashboards:</strong> Dedicated company profiles consolidating recruitment history, eligibility, rounds, and question banks.
              </div>
            </div>
            <div className="about-bullet-box">
              <GraduationCap size={16} className="text-purple" />
              <div>
                <strong>Eligibility & Backlog Analytics:</strong> Company-wise eligibility grouping for quick filtering during recruitment eligibility checks.
              </div>
            </div>
          </div>
        </section>

        {/* 7. TECHNOLOGY STACK */}
        <section className="about-section">
          <div className="about-section-header">
            <div className="about-icon-box blue">
              <Code2 size={22} />
            </div>
            <div>
              <h2>7. Technology Stack</h2>
              <p>Verified stack implemented in this repository</p>
            </div>
          </div>
          <div className="about-tech-grid">
            <div className="tech-badge-card">
              <span className="tech-tag-title">Frontend UI</span>
              <strong>React 19 + Vite</strong>
              <small>React Router 7 • Recharts • Lucide Icons</small>
            </div>
            <div className="tech-badge-card">
              <span className="tech-tag-title">REST API Backend</span>
              <strong>Python FastAPI</strong>
              <small>Pydantic • Uvicorn • CORS Middleware</small>
            </div>
            <div className="tech-badge-card">
              <span className="tech-tag-title">NLP Pipeline</span>
              <strong>Python Regex & Rule Engine</strong>
              <small>Text Cleaning • Entity Extraction • Deduplication</small>
            </div>
            <div className="tech-badge-card">
              <span className="tech-tag-title">Database</span>
              <strong>PostgreSQL Database</strong>
              <small>SQLAlchemy ORM • Relational Schema</small>
            </div>
            <div className="tech-badge-card">
              <span className="tech-tag-title">Message Ingestion</span>
              <strong>Telethon Telegram Ingestion</strong>
              <small>Authorized Message Staging Client</small>
            </div>
          </div>
        </section>

        {/* 8. INTENDED USERS */}
        <section className="about-section">
          <div className="about-section-header">
            <div className="about-icon-box green">
              <Users size={22} />
            </div>
            <div>
              <h2>8. Intended Stakeholders</h2>
              <p>Target user roles across campus recruitment</p>
            </div>
          </div>
          <div className="about-grid-3">
            <div className="user-role-card">
              <GraduationCap size={24} className="text-green" />
              <h3>Students</h3>
              <p>Access historical interview questions, topic frequency trends, and company round structures to prepare efficiently for upcoming drives.</p>
            </div>
            <div className="user-role-card">
              <Brain size={24} className="text-green" />
              <h3>Faculty Mentors</h3>
              <p>Identify curriculum skill gaps based on real-world industry technical topics and monitor candidate placement preparation readiness.</p>
            </div>
            <div className="user-role-card">
              <Building2 size={24} className="text-green" />
              <h3>Placement Officers</h3>
              <p>Review structured company drive statistics, track reported eligibility criteria, and export official placement summary reports.</p>
            </div>
          </div>
        </section>

        {/* 9. ACADEMIC CONTEXT */}
        <section className="about-section academic-section">
          <div className="about-section-header">
            <div className="about-icon-box purple">
              <GraduationCap size={22} />
            </div>
            <div>
              <h2>9. Academic Context & Batch Scope</h2>
              <p>Engineering project background</p>
            </div>
          </div>
          <div className="academic-box">
            <p>
              This system is developed as a <strong>Final Year Computer Science & Engineering (B.E. CSE) Capstone Project</strong> for the <strong>2023–2027 Batch Cycle</strong>.
            </p>
            <div className="academic-meta-pills">
              <span>Department of Computer Science & Engineering</span>
              <span>•</span>
              <span>B.E. CSE 2023–2027 Cycle</span>
              <span>•</span>
              <span>Placement Intelligence Subsystem</span>
            </div>
          </div>
        </section>

        {/* FOOTER AUTHORIZATION NOTE */}
        <div className="about-note">
          <ShieldCheck size={20} className="text-indigo" />
          <div>
            <strong>Authorized Data Processing Compliance</strong>
            <p>
              The Placement Feedback Intelligence system processes feedback data collected exclusively from authorized departmental Telegram channels and student submission forms in accordance with project guidelines.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
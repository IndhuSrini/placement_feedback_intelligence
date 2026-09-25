import { Link } from 'react-router-dom'

const Footer = () => (
  <footer className="site-footer">
    <div className="container footer-grid">
      <div>
        <h4>Placement Feedback Intelligence</h4>
        <p>
          An AI-powered platform converting placement feedback into structured intelligence for colleges,
          recruiters, and students.
        </p>
      </div>

      <div>
        <h5>Navigation</h5>
        <ul>
          <li><Link to="/">Home</Link></li>
          <li><Link to="/companies">Companies</Link></li>
          <li><Link to="/analytics">Analytics</Link></li>
          <li><Link to="/questions">Question Bank</Link></li>
          <li><Link to="/about">About</Link></li>
        </ul>
      </div>

      <div>
        <h5>Project</h5>
        <ul>
          <li>2023–27 batch</li>
          <li>Prototype demonstration</li>
          <li>Synthetic placement data</li>
        </ul>
      </div>

      <div>
        <h5>Technology</h5>
        <ul>
          <li>React + Vite</li>
          <li>FastAPI + Python</li>
          <li>PostgreSQL</li>
          <li>AI/NLP pipeline</li>
        </ul>
      </div>
    </div>

    <div className="container footer-bottom">
      <span>Prototype data notice: This demo uses synthetic placement feedback for development and education purposes.</span>
      <span>© 2026 Placement Feedback Intelligence</span>
    </div>
  </footer>
)

export default Footer

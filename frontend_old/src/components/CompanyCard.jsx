import { ArrowRight, Building2, CheckCircle2 } from 'lucide-react'
import { Link } from 'react-router-dom'

const CompanyCard = ({ company }) => {
  const driveCount = company.placement_drives ?? company.drive_count ?? 0
  const questionCount = company.questions ?? company.question_count ?? 0
  const topicCount = company.topics ?? company.topic_count ?? 0

  return (
    <div className="company-card">
      <div className="company-card-header">
        <div className="company-badge">
          <Building2 size={18} />
        </div>
        <span className="company-pill">Placement intelligence</span>
      </div>

      <h3>{company.name || 'Unnamed company'}</h3>

      <div className="company-metrics">
        <div>
          <span>Drives</span>
          <strong>{driveCount}</strong>
        </div>
        <div>
          <span>Questions</span>
          <strong>{questionCount}</strong>
        </div>
        <div>
          <span>Topics</span>
          <strong>{topicCount}</strong>
        </div>
      </div>

      <div className="company-eligibility">
        <CheckCircle2 size={16} />
        <span>{company.eligibility_summary || 'Eligibility summary not available'}</span>
      </div>

      <Link to={`/companies/${company.id}`} className="link-button">
        View Insights <ArrowRight size={16} />
      </Link>
    </div>
  )
}

export default CompanyCard

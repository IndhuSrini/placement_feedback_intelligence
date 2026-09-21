import { ArrowUpRight } from 'lucide-react'

const StatCard = ({ label, value, icon: Icon, accent = 'blue' }) => (
  <div className={`stat-card accent-${accent}`}>
    <div className="stat-card-header">
      <div className="stat-icon-wrap">
        <Icon size={18} />
      </div>
      <ArrowUpRight size={16} className="stat-arrow" />
    </div>
    <div className="stat-value">{value}</div>
    <div className="stat-label">{label}</div>
  </div>
)

export default StatCard

const InsightCard = ({ title, description, icon: Icon }) => (
  <div className="insight-card">
    <div className="insight-icon-wrap">
      <Icon size={18} />
    </div>
    <div>
      <h4>{title}</h4>
      <p>{description}</p>
    </div>
  </div>
)

export default InsightCard

const TopicCard = ({ topic, index }) => (
  <div className="topic-card" style={{ animationDelay: `${index * 80}ms` }}>
    <div className="topic-header">
      <span className="topic-rank">#{index + 1}</span>
      <span className="topic-category">{topic.category || 'General'}</span>
    </div>
    <h4>{topic.topic || 'Unnamed topic'}</h4>
    <div className="topic-bar">
      <div className="topic-bar-fill" style={{ width: `${Math.max((topic.occurrence_count / 10) * 100, 18)}%` }} />
    </div>
    <div className="topic-meta">{topic.occurrence_count || 0} mentions</div>
  </div>
)

export default TopicCard

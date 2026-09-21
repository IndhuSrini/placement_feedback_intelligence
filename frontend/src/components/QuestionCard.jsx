import { BadgeCheck, MessageSquareText } from 'lucide-react'
import { getDifficultyColor } from '../utils/formatting'

const QuestionCard = ({ question }) => (
  <div className="question-card">
    <div className="question-card-top">
      <div className="icon-box soft">
        <MessageSquareText size={16} />
      </div>
      <span className="difficulty-pill" style={{ background: `${getDifficultyColor(question.difficulty)}20`, color: getDifficultyColor(question.difficulty) }}>
        {question.difficulty || 'Not available'}
      </span>
    </div>

    <h4>{question.question || 'Untitled question'}</h4>

    <div className="question-meta-row">
      <span>{question.topic || 'General topic'}</span>
      <span>{question.category || 'General category'}</span>
    </div>

    <div className="question-footer">
      <span>Frequency: {question.occurrence_count || 1}</span>
      <span className="verified-chip">
        <BadgeCheck size={14} />
        {question.verification_status || 'Unverified'}
      </span>
    </div>
  </div>
)

export default QuestionCard

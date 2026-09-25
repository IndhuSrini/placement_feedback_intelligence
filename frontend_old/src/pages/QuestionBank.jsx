import { useEffect, useMemo, useState } from 'react'
import { Search } from 'lucide-react'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingState from '../components/LoadingState'
import { fetchFrequentQuestions } from '../services/api'

const QuestionBank = ({ globalSearch }) => {
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [topicFilter, setTopicFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [difficultyFilter, setDifficultyFilter] = useState('all')
  const [visibleCount, setVisibleCount] = useState(12)

  useEffect(() => {
    const loadQuestions = async () => {
      try {
        setLoading(true)
        const response = await fetchFrequentQuestions()
        setQuestions(response.data || [])
      } catch (err) {
        setError('Unable to load the question bank. Check the backend API connection.')
      } finally {
        setLoading(false)
      }
    }

    loadQuestions()
  }, [])

  const filters = useMemo(() => {
    const query = (globalSearch || '').trim().toLowerCase()

    return questions.filter((question) => {
      const topicMatch = topicFilter === 'all' || (question.topic || '').toLowerCase() === topicFilter.toLowerCase()
      const categoryMatch = categoryFilter === 'all' || (question.category || '').toLowerCase() === categoryFilter.toLowerCase()
      const difficultyMatch = difficultyFilter === 'all' || (question.difficulty || '').toLowerCase() === difficultyFilter.toLowerCase()
      const searchMatch = !query || (question.question || '').toLowerCase().includes(query)
      return topicMatch && categoryMatch && difficultyMatch && searchMatch
    })
  }, [categoryFilter, difficultyFilter, globalSearch, questions, topicFilter])

  const visibleQuestions = filters.slice(0, visibleCount)
  const uniqueTopics = [...new Set(questions.map((item) => item.topic).filter(Boolean))]
  const uniqueCategories = [...new Set(questions.map((item) => item.category).filter(Boolean))]
  const uniqueDifficulties = [...new Set(questions.map((item) => item.difficulty).filter(Boolean))]

  if (loading) return <LoadingState message="Loading question bank..." />
  if (error) return <ErrorState message={error} />

  return (
    <div className="page-shell container">
      <div className="inner-page-header">
        <div>
          <p className="section-kicker">Question bank</p>
          <h1>Placement Question Bank</h1>
          <p className="page-intro">Explore frequently discussed interview and assessment questions extracted from placement feedback.</p>
        </div>
      </div>

      <div className="filter-grid">
        <div className="search-box minimal">
          <Search size={16} />
          <input type="text" value={globalSearch} readOnly placeholder="Search questions from the header" />
        </div>

        <select value={topicFilter} onChange={(e) => setTopicFilter(e.target.value)}>
          <option value="all">All topics</option>
          {uniqueTopics.map((topic) => (
            <option key={topic} value={topic}>{topic}</option>
          ))}
        </select>

        <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          <option value="all">All categories</option>
          {uniqueCategories.map((category) => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>

        <select value={difficultyFilter} onChange={(e) => setDifficultyFilter(e.target.value)}>
          <option value="all">All difficulties</option>
          {uniqueDifficulties.map((difficulty) => (
            <option key={difficulty} value={difficulty}>{difficulty}</option>
          ))}
        </select>
      </div>

      <div className="question-bank-table-wrap">
        <table className="question-bank-table">
          <thead>
            <tr>
              <th>Question</th>
              <th>Topic</th>
              <th>Category</th>
              <th>Difficulty</th>
              <th>Frequency</th>
            </tr>
          </thead>
          <tbody>
            {visibleQuestions.length > 0 ? visibleQuestions.map((question, index) => (
              <tr key={`${question.id}-${index}`}>
                <td>{question.question || 'Untitled question'}</td>
                <td>{question.topic || 'Not available'}</td>
                <td>{question.category || 'Not available'}</td>
                <td>{question.difficulty || 'Not available'}</td>
                <td>{question.occurrence_count || 1}</td>
              </tr>
            )) : (
              <tr>
                <td colSpan="5">
                  <EmptyState title="No matching questions" message="Adjust your search or filters to view more question data." />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {visibleCount < filters.length && (
        <div className="load-more-wrap">
          <button className="secondary-button" onClick={() => setVisibleCount((count) => count + 12)}>Load more</button>
        </div>
      )}
    </div>
  )
}

export default QuestionBank

import { useEffect, useMemo, useState } from 'react'
import { BarChart3, CircleDashed, Database, Filter, MessageSquareText, Presentation, ShieldCheck } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingState from '../components/LoadingState'
import { fetchCategories, fetchConfidence, fetchEligibility, fetchFrequentQuestions, fetchFrequentTopics, fetchOverview, fetchYearWise } from '../services/api'

const COLORS = ['#2563eb', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#0ea5e9']

const Analytics = () => {
  const [overview, setOverview] = useState(null)
  const [topics, setTopics] = useState([])
  const [questions, setQuestions] = useState([])
  const [categories, setCategories] = useState([])
  const [confidence, setConfidence] = useState(null)
  const [yearWise, setYearWise] = useState([])
  const [eligibility, setEligibility] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoading(true)
        setError('')

        const [overviewRes, topicsRes, questionsRes, categoriesRes, confidenceRes, yearRes, eligibilityRes] = await Promise.all([
          fetchOverview(),
          fetchFrequentTopics(),
          fetchFrequentQuestions(),
          fetchCategories(),
          fetchConfidence(),
          fetchYearWise(),
          fetchEligibility()
        ])

        setOverview(overviewRes.data || {})
        setTopics((topicsRes.data || []).slice(0, 8))
        setQuestions((questionsRes.data || []).slice(0, 8))
        setCategories(categoriesRes.data || [])
        setConfidence(confidenceRes.data || null)
        setYearWise(yearRes.data || [])
        setEligibility((eligibilityRes.data || []).slice(0, 10))
      } catch (err) {
        setError('Analytics data could not be loaded. Please ensure the backend is running and accessible.')
      } finally {
        setLoading(false)
      }
    }

    loadAnalytics()
  }, [])

  const averageCgpa = useMemo(() => {
    const validValues = (eligibility || []).map((item) => item.minimum_cgpa).filter((value) => value !== null && value !== undefined)
    if (!validValues.length) return 'Not available'
    return (validValues.reduce((sum, value) => sum + Number(value), 0) / validValues.length).toFixed(2)
  }, [eligibility])

  if (loading) return <LoadingState message="Loading analytics workspace..." />
  if (error) return <ErrorState message={error} />

  return (
    <div className="page-shell container analytics-page">
      <div className="inner-page-header">
        <div>
          <p className="section-kicker">Analytics workspace</p>
          <h1>Placement analytics</h1>
          <p className="page-intro">Monitor recruitment trends, common topics, question patterns, and eligibility signals across the collected placement data.</p>
        </div>
      </div>

      <div className="stats-grid analytics-grid">
        <div className="stat-card accent-blue">
          <div className="stat-card-header"><div className="stat-icon-wrap"><BarChart3 size={18} /></div></div>
          <div className="stat-value">{overview?.total_companies ?? 'Not available'}</div>
          <div className="stat-label">Companies covered</div>
        </div>
        <div className="stat-card accent-green">
          <div className="stat-card-header"><div className="stat-icon-wrap"><Presentation size={18} /></div></div>
          <div className="stat-value">{overview?.total_placement_drives ?? 'Not available'}</div>
          <div className="stat-label">Placement drives</div>
        </div>
        <div className="stat-card accent-purple">
          <div className="stat-card-header"><div className="stat-icon-wrap"><MessageSquareText size={18} /></div></div>
          <div className="stat-value">{overview?.total_questions ?? 'Not available'}</div>
          <div className="stat-label">Questions analyzed</div>
        </div>
      </div>

      <div className="two-column-layout">
        <section className="content-panel">
          <div className="panel-header-row"><h3>Placement landscape</h3></div>
          <div className="chart-panel">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={yearWise}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="placement_drives" fill="#2563eb" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="content-panel">
          <div className="panel-header-row"><h3>Topic intelligence</h3></div>
          <div className="chart-panel">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={categories} dataKey="occurrence_count" nameKey="category" outerRadius={80} label>
                  {categories.map((entry, index) => (
                    <Cell key={`${entry.category}-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Legend />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      <div className="two-column-layout">
        <section className="content-panel">
          <div className="panel-header-row"><h3>Most frequent topics</h3></div>
          <div className="list-stack">
            {topics.length > 0 ? topics.map((topic, index) => (
              <div key={`${topic.topic}-${index}`} className="simple-list-row">
                <span>{index + 1}. {topic.topic}</span>
                <strong>{topic.occurrence_count} mentions</strong>
              </div>
            )) : <EmptyState title="No topic data" message="No recurring topics are available yet." />}
          </div>
        </section>

        <section className="content-panel">
          <div className="panel-header-row"><h3>Frequently asked questions</h3></div>
          <div className="list-stack">
            {questions.length > 0 ? questions.map((question, index) => (
              <div key={`${question.id}-${index}`} className="simple-list-row columned">
                <span>{question.question}</span>
                <small>{question.difficulty || 'Difficulty not available'}</small>
              </div>
            )) : <EmptyState title="No questions found" message="No repeated question patterns are currently available." />}
          </div>
        </section>
      </div>

      <div className="two-column-layout">
        <section className="content-panel">
          <div className="panel-header-row"><h3>Eligibility analysis</h3></div>
          <div className="list-stack">
            <div className="simple-list-row">
              <span>Average minimum CGPA</span>
              <strong>{averageCgpa}</strong>
            </div>
            {eligibility.map((item, index) => (
              <div key={`${item.company}-${item.year}-${index}`} className="simple-list-row columned">
                <span>{item.company}</span>
                <small>CGPA ≥ {item.minimum_cgpa ?? 'Not available'} • Backlogs ≤ {item.maximum_backlogs ?? 'Not available'}</small>
              </div>
            ))}
          </div>
        </section>

        <section className="content-panel">
          <div className="panel-header-row"><h3>Feedback quality</h3></div>
          <div className="confidence-box">
            <div className="confidence-stat">
              <Database size={18} />
              <span>Total questions</span>
              <strong>{confidence?.total_questions ?? 0}</strong>
            </div>
            <div className="confidence-stat">
              <ShieldCheck size={18} />
              <span>Average confidence</span>
              <strong>{confidence?.average_confidence ?? 0}%</strong>
            </div>
            <div className="confidence-stat">
              <CircleDashed size={18} />
              <span>Verified questions</span>
              <strong>{confidence?.verified_questions ?? 0}</strong>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

export default Analytics

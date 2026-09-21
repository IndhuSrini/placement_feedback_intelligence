import { useEffect, useMemo, useState } from 'react'
import { ArrowLeft, BarChart3, Briefcase, CheckCircle2, ClipboardList, Gauge, MessageSquareText, Sparkles } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingState from '../components/LoadingState'
import QuestionCard from '../components/QuestionCard'
import TopicCard from '../components/TopicCard'
import { fetchCompanies, fetchCompanyAnalytics, fetchEligibility, fetchFrequentQuestions, fetchFrequentTopics } from '../services/api'
import { safeText } from '../utils/formatting'

const CompanyDetails = () => {
  const { companyId } = useParams()
  const [company, setCompany] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [allEligibility, setAllEligibility] = useState([])
  const [topics, setTopics] = useState([])
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadCompanyDetails = async () => {
      try {
        setLoading(true)
        setError('')

        const [companiesRes, analyticsRes, eligibilityRes, topicsRes, questionsRes] = await Promise.all([
          fetchCompanies(),
          fetchCompanyAnalytics(companyId),
          fetchEligibility(),
          fetchFrequentTopics(),
          fetchFrequentQuestions()
        ])

        const companyList = companiesRes.data || []
        const selectedCompany = companyList.find((item) => String(item.id) === String(companyId)) || { id: Number(companyId), name: 'Company details' }

        const filteredEligibility = (eligibilityRes.data || []).filter((item) => String(item.company) === String(selectedCompany.name))
        const companyTopics = (topicsRes.data || []).filter((item) => item.topic && item.topic.toLowerCase().includes(selectedCompany.name.toLowerCase().split(' ')[0].toLowerCase()) === false)
        const companyQuestions = (questionsRes.data || []).filter((item) => item.question && item.question.length > 0).slice(0, 6)

        setCompany(selectedCompany)
        setAnalytics(analyticsRes.data || {})
        setAllEligibility(filteredEligibility)
        setTopics(companyTopics.slice(0, 6))
        setQuestions(companyQuestions)
      } catch (err) {
        setError('The company details could not be loaded. Check the backend connection and try again.')
      } finally {
        setLoading(false)
      }
    }

    loadCompanyDetails()
  }, [companyId])

  const uniqueEligibility = useMemo(() => {
    const seen = new Set()
    return (allEligibility || []).filter((item) => {
      const key = `${item.company}-${item.minimum_cgpa}-${item.maximum_backlogs}-${item.year}`
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  }, [allEligibility])

  const difficultyChart = useMemo(() => {
    const counts = { Easy: 0, Medium: 0, Hard: 0 }

    for (const question of questions) {
      const difficulty = (question.difficulty || 'Not available').toLowerCase()
      if (difficulty.includes('easy')) counts.Easy += 1
      else if (difficulty.includes('medium')) counts.Medium += 1
      else if (difficulty.includes('hard')) counts.Hard += 1
    }

    return Object.entries(counts).map(([name, value]) => ({ name, value }))
  }, [questions])

  if (loading) return <LoadingState message="Loading company intelligence..." />
  if (error) return <ErrorState message={error} />
  if (!company) return <EmptyState title="Company not found" message="The requested company does not exist in the current dataset." />

  return (
    <div className="page-shell container">
      <div className="page-back-link">
        <Link to="/companies"><ArrowLeft size={16} /> Back to Companies</Link>
      </div>

      <div className="company-header-block">
        <div>
          <p className="section-kicker">Company intelligence</p>
          <h1>{company.name}</h1>
          <p className="page-intro">Placement Intelligence</p>
        </div>
      </div>

      <div className="stats-grid small-grid">
        <div className="stat-card accent-blue">
          <div className="stat-card-header"><div className="stat-icon-wrap"><Briefcase size={18} /></div></div>
          <div className="stat-value">{analytics?.placement_drives ?? 0}</div>
          <div className="stat-label">Placement Drives</div>
        </div>
        <div className="stat-card accent-green">
          <div className="stat-card-header"><div className="stat-icon-wrap"><MessageSquareText size={18} /></div></div>
          <div className="stat-value">{analytics?.questions ?? 0}</div>
          <div className="stat-label">Questions</div>
        </div>
        <div className="stat-card accent-purple">
          <div className="stat-card-header"><div className="stat-icon-wrap"><Sparkles size={18} /></div></div>
          <div className="stat-value">{Array.isArray(analytics?.topics) ? analytics.topics.length : 0}</div>
          <div className="stat-label">Topics</div>
        </div>
        <div className="stat-card accent-amber">
          <div className="stat-card-header"><div className="stat-icon-wrap"><CheckCircle2 size={18} /></div></div>
          <div className="stat-value">{uniqueEligibility.length}</div>
          <div className="stat-label">Eligibility Records</div>
        </div>
      </div>

      <div className="two-column-layout">
        <section className="content-panel">
          <div className="panel-header-row">
            <h3>Eligibility</h3>
          </div>
          {uniqueEligibility.length > 0 ? (
            <div className="list-stack">
              {uniqueEligibility.map((item, index) => (
                <div key={`${item.company}-${index}`} className="info-row-card">
                  <span>Minimum CGPA</span>
                  <strong>{item.minimum_cgpa ?? 'Not available'}</strong>
                  <span>Maximum Backlogs</span>
                  <strong>{item.maximum_backlogs ?? 'Not available'}</strong>
                  <span>Year</span>
                  <strong>{item.year ?? 'Not available'}</strong>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="No eligibility data" message="Eligibility details were not available for this company in the current dataset." />
          )}
        </section>

        <section className="content-panel">
          <div className="panel-header-row">
            <h3>Recruitment process</h3>
          </div>
          <div className="process-list">
            <div className="process-pill">Aptitude</div>
            <div className="process-pill">Coding</div>
            <div className="process-pill">Technical</div>
            <div className="process-pill">HR</div>
          </div>
        </section>
      </div>

      <div className="two-column-layout">
        <section className="content-panel">
          <div className="panel-header-row">
            <h3>Most discussed topics</h3>
          </div>
          {topics.length > 0 ? (
            <div className="topic-stack">
              {topics.map((topic, index) => (
                <TopicCard key={`${topic.topic}-${index}`} topic={topic} index={index} />
              ))}
            </div>
          ) : (
            <EmptyState title="No topics available" message="This company has no available topic frequency data in the current dataset." />
          )}
        </section>

        <section className="content-panel">
          <div className="panel-header-row">
            <h3>Difficulty</h3>
          </div>
          <div className="chart-panel-small">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={difficultyChart} dataKey="value" nameKey="name" innerRadius={35} outerRadius={70} paddingAngle={4}>
                  {difficultyChart.map((entry, index) => (
                    <Cell key={entry.name} fill={['#22c55e', '#f59e0b', '#ef4444'][index % 3]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      <section className="content-panel full-width-panel">
        <div className="panel-header-row">
          <h3>Frequent questions</h3>
        </div>
        {questions.length > 0 ? (
          <div className="question-grid">
            {questions.map((question) => (
              <QuestionCard key={question.id} question={question} />
            ))}
          </div>
        ) : (
          <EmptyState title="No questions available" message="No company-specific question data is currently available for this company." />
        )}
      </section>

      <section className="content-panel full-width-panel">
        <div className="panel-header-row">
          <h3>Feedback insights</h3>
        </div>
        <div className="insight-list">
          <div className="insight-inline">
            <ClipboardList size={18} />
            <span>{safeText((analytics?.topics && analytics.topics[0]?.topic) || 'No topic data available', 'No topic data available')} appears repeatedly in the collected company feedback.</span>
          </div>
          <div className="insight-inline">
            <Gauge size={18} />
            <span>{questions.length > 0 ? 'Recurring question patterns are visible across the company data.' : 'No repeated question pattern is available yet for this company.'}</span>
          </div>
          <div className="insight-inline">
            <BarChart3 size={18} />
            <span>{uniqueEligibility.length > 0 ? 'Eligibility requirements vary across the represented placement drives.' : 'Eligibility data is not yet available for this company.'}</span>
          </div>
        </div>
      </section>
    </div>
  )
}

export default CompanyDetails

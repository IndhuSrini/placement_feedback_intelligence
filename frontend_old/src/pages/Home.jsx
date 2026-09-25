import { useEffect, useMemo, useState } from 'react'
import { ArrowRight, BarChart3, BookOpenText, BrainCircuit, Building2, CheckCircle2, ChevronRight, Database, FileText, MessageSquareText, Network, ShieldCheck, Sparkles, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'
import CompanyCard from '../components/CompanyCard'
import InsightCard from '../components/InsightCard'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import QuestionCard from '../components/QuestionCard'
import StatCard from '../components/StatCard'
import TopicCard from '../components/TopicCard'
import { fetchCompanies, fetchFrequentQuestions, fetchFrequentTopics, fetchOverview } from '../services/api'

const processSteps = [
  { label: 'Telegram Feedback', icon: MessageSquareText },
  { label: 'Message Collection', icon: Database },
  { label: 'NLP Extraction', icon: BrainCircuit },
  { label: 'Information Classification', icon: FileText },
  { label: 'Duplicate Detection', icon: ShieldCheck },
  { label: 'PostgreSQL', icon: Database },
  { label: 'Analytics & Insights', icon: BarChart3 }
]

const Home = ({ globalSearch }) => {
  const [overview, setOverview] = useState(null)
  const [topicData, setTopicData] = useState([])
  const [questions, setQuestions] = useState([])
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        setError('')

        const [overviewRes, topicRes, questionRes, companyRes] = await Promise.all([
          fetchOverview(),
          fetchFrequentTopics(),
          fetchFrequentQuestions(),
          fetchCompanies()
        ])

        setOverview(overviewRes.data)
        setTopicData(topicRes.data || [])
        setQuestions((questionRes.data || []).slice(0, 4))
        setCompanies((companyRes.data || []).slice(0, 6))
      } catch (err) {
        console.error('Failed to load homepage data from FastAPI', {
          endpoints: [
            '/analytics/overview',
            '/analytics/frequent-topics',
            '/analytics/frequent-questions',
            '/companies/'
          ],
          error: err
        })
        setError('Unable to load the homepage data. Please verify the FastAPI server is running on http://127.0.0.1:8000. Check the browser console for the underlying error.')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  const filteredCompanies = useMemo(() => {
    const query = (globalSearch || '').trim().toLowerCase()

    if (!query) return companies

    return companies.filter((company) =>
      (company.name || '').toLowerCase().includes(query)
    )
  }, [companies, globalSearch])

  const filteredTopics = useMemo(() => {
    const query = (globalSearch || '').trim().toLowerCase()

    if (!query) return topicData.slice(0, 6)

    return topicData.filter((topic) => (topic.topic || '').toLowerCase().includes(query))
  }, [globalSearch, topicData])

  if (loading) return <LoadingState message="Loading placement intelligence overview..." />
  if (error) return <ErrorState message={error} />

  return (
    <div className="page-shell">
      <section className="hero-section container">
        <div className="hero-copy">
          <div className="eyebrow">
            <Sparkles size={14} />
            AI-powered placement intelligence
          </div>
          <h1>Turn Placement Feedback into Actionable Intelligence</h1>
          <p>
            An AI-powered platform that transforms unstructured placement feedback into organized recruitment insights,
            frequently discussed topics, questions, and company-wise intelligence.
          </p>
          <div className="hero-actions">
            <Link to="/companies" className="primary-button">Explore Companies</Link>
            <Link to="/analytics" className="secondary-button">View Analytics</Link>
          </div>
        </div>

        <div className="hero-visual">
          <div className="visual-card large-card">
            <div className="visual-header">
              <span className="dot green" />
              <span className="dot yellow" />
              <span className="dot red" />
            </div>
            <div className="mini-chart">
              <div className="mini-bars">
                {[26, 42, 36, 58, 74, 68, 90].map((value, index) => (
                  <span key={index} style={{ height: `${value}%` }} />
                ))}
              </div>
              <div className="pulse-box">
                <TrendingUp size={18} />
                <span>Insights live</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="container section-gap">
        <div className="section-heading-row">
          <div>
            <p className="section-kicker">Overview</p>
            <h2>Placement landscape</h2>
          </div>
        </div>

        <div className="stats-grid">
          <StatCard label="Companies Covered" value={overview?.total_companies ?? 'Not available'} icon={Building2} accent="blue" />
          <StatCard label="Placement Drives" value={overview?.total_placement_drives ?? 'Not available'} icon={TrendingUp} accent="green" />
          <StatCard label="Questions Analyzed" value={overview?.total_questions ?? 'Not available'} icon={FileText} accent="purple" />
          <StatCard label="Topics Identified" value={overview?.total_topics ?? 'Not available'} icon={Network} accent="amber" />
        </div>
      </section>

      <section className="container section-gap">
        <div className="section-heading-row">
          <div>
            <p className="section-kicker">Topic intelligence</p>
            <h2>Most discussed topics</h2>
          </div>
          <Link to="/analytics" className="text-link">View analytics <ChevronRight size={16} /></Link>
        </div>

        <div className="topic-grid">
          {filteredTopics.length > 0 ? filteredTopics.map((topic, index) => (
            <TopicCard key={`${topic.topic}-${index}`} topic={topic} index={index} />
          )) : <EmptyState message="No topics match the current search." title="No matching topics" />}
        </div>
      </section>

      <section className="container section-gap">
        <div className="section-heading-row">
          <div>
            <p className="section-kicker">Question intelligence</p>
            <h2>Questions students keep discussing</h2>
          </div>
          <Link to="/questions" className="text-link">View Question Bank <ChevronRight size={16} /></Link>
        </div>

        <div className="question-grid">
          {questions.length > 0 ? questions.map((question) => (
            <QuestionCard key={question.id} question={question} />
          )) : <EmptyState title="No questions available" message="No frequently discussed questions were found." />}
        </div>
      </section>

      <section className="container section-gap">
        <div className="section-heading-row">
          <div>
            <p className="section-kicker">Companies</p>
            <h2>Company overview</h2>
          </div>
          <Link to="/companies" className="text-link">Explore all <ChevronRight size={16} /></Link>
        </div>

        <div className="company-grid">
          {filteredCompanies.length > 0 ? filteredCompanies.map((company) => (
            <CompanyCard key={company.id} company={company} />
          )) : <EmptyState title="No companies match the current search" message="Try a different company name or clear the search." />}
        </div>
      </section>

      <section className="container section-gap">
        <div className="section-heading-row">
          <div>
            <p className="section-kicker">Workflow</p>
            <h2>How it works</h2>
          </div>
        </div>

        <div className="process-flow">
          {processSteps.map((step, index) => (
            <div key={step.label} className="process-step">
              <div className="process-node">
                <step.icon size={18} />
              </div>
              {index < processSteps.length - 1 && <div className="process-arrow">↓</div>}
              <span>{step.label}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="container section-gap bottom-pad">
        <div className="section-heading-row">
          <div>
            <p className="section-kicker">Why this platform</p>
            <h2>Built for better placement preparation</h2>
          </div>
        </div>

        <div className="insights-grid">
          <InsightCard title="Structured Feedback" description="Raw campus conversations become clean, searchable recruitment intelligence." icon={BookOpenText} />
          <InsightCard title="AI-powered Extraction" description="The NLP layer identifies trends, topics, and repeated questions from unstructured messages." icon={BrainCircuit} />
          <InsightCard title="Company-wise Intelligence" description="Compare eligibility, recurring questions, and mutually discussed topics across companies." icon={Building2} />
          <InsightCard title="Data-driven Preparation" description="Students can prepare with grounded patterns from the collected placement experience data." icon={CheckCircle2} />
        </div>
      </section>
    </div>
  )
}

export default Home

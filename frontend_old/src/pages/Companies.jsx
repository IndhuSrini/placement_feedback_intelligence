import { useEffect, useMemo, useState } from 'react'
import { Search } from 'lucide-react'
import CompanyCard from '../components/CompanyCard'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingState from '../components/LoadingState'
import { fetchCompanies, fetchCompanyAnalytics } from '../services/api'

const Companies = ({ globalSearch }) => {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadCompanies = async () => {
      try {
        setLoading(true)
        setError('')

        const companiesResponse = await fetchCompanies()
        const companyData = companiesResponse.data || []

        const enriched = await Promise.all(
          companyData.map(async (company) => {
            try {
              const analyticsResponse = await fetchCompanyAnalytics(company.id)
              const analytics = analyticsResponse.data || {}
              return {
                ...company,
                placement_drives: analytics.placement_drives ?? 0,
                questions: analytics.questions ?? 0,
                topics: Array.isArray(analytics.topics) ? analytics.topics.length : 0,
                eligibility_summary: analytics.eligibility_summary || 'Eligibility details not available'
              }
            } catch {
              return {
                ...company,
                placement_drives: 0,
                questions: 0,
                topics: 0,
                eligibility_summary: 'Eligibility details not available'
              }
            }
          })
        )

        setCompanies(enriched)
      } catch (err) {
        setError('Unable to load companies. Please check that the backend is running.')
      } finally {
        setLoading(false)
      }
    }

    loadCompanies()
  }, [])

  const filteredCompanies = useMemo(() => {
    const query = (globalSearch || '').trim().toLowerCase()

    if (!query) return companies

    return companies.filter((company) =>
      (company.name || '').toLowerCase().includes(query)
    )
  }, [companies, globalSearch])

  if (loading) return <LoadingState message="Loading company intelligence..." />
  if (error) return <ErrorState message={error} />

  return (
    <div className="page-shell container">
      <div className="inner-page-header">
        <div>
          <p className="section-kicker">Companies</p>
          <h1>Explore Companies</h1>
          <p className="page-intro">
            Explore placement feedback, eligibility information, frequently discussed topics, and interview questions company by company.
          </p>
        </div>
      </div>

      <div className="search-panel">
        <div className="search-box">
          <Search size={16} />
          <input
            type="text"
            value={globalSearch}
            readOnly
            placeholder="Search companies using the global header"
          />
        </div>
      </div>

      <div className="company-grid">
        {filteredCompanies.length > 0 ? filteredCompanies.map((company) => (
          <CompanyCard key={company.id} company={company} />
        )) : <EmptyState title="No companies found" message="Try updating your search or return later for more placement data." />}
      </div>
    </div>
  )
}

export default Companies

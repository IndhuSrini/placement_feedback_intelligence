import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000'
})

export const fetchOverview = () => api.get('/analytics/overview')
export const fetchFrequentTopics = () => api.get('/analytics/frequent-topics')
export const fetchFrequentQuestions = () => api.get('/analytics/frequent-questions')
export const fetchCategories = () => api.get('/analytics/categories')
export const fetchConfidence = () => api.get('/analytics/confidence')
export const fetchYearWise = () => api.get('/analytics/year-wise')
export const fetchEligibility = () => api.get('/analytics/eligibility')
export const fetchCompanies = () => api.get('/companies/')
export const fetchPlacementDrives = () => api.get('/placement-drives/')
export const fetchCompanyAnalytics = (companyId) => api.get(`/analytics/company/${companyId}`)

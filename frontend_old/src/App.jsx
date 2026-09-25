import { useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import Home from './pages/Home'
import Companies from './pages/Companies'
import CompanyDetails from './pages/CompanyDetails'
import Analytics from './pages/Analytics'
import QuestionBank from './pages/QuestionBank'
import About from './pages/About'

function App() {
  const [globalSearch, setGlobalSearch] = useState('')

  return (
    <div className="app-layout">
      <Header globalSearch={globalSearch} setGlobalSearch={setGlobalSearch} />

      <main className="site-main">
        <Routes>
          <Route path="/" element={<Home globalSearch={globalSearch} />} />
          <Route path="/companies" element={<Companies globalSearch={globalSearch} />} />
          <Route path="/companies/:companyId" element={<CompanyDetails />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/questions" element={<QuestionBank globalSearch={globalSearch} />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <Footer />
    </div>
  )
}

export default App

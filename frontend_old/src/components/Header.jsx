import { Link, NavLink } from 'react-router-dom'
import { Search, Sparkles } from 'lucide-react'

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Companies', to: '/companies' },
  { label: 'Analytics', to: '/analytics' },
  { label: 'Question Bank', to: '/questions' },
  { label: 'About', to: '/about' }
]

const Header = ({ globalSearch, setGlobalSearch }) => (
  <header className="site-header">
    <div className="container header-inner">
      <Link to="/" className="brand-wrap">
        <div className="brand-mark">
          <Sparkles size={18} />
        </div>
        <div>
          <span className="brand-name">Placement Feedback Intelligence</span>
        </div>
      </Link>

      <nav className="main-nav" aria-label="Main navigation">
        {navItems.map((item) => (
          <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="header-actions">
        <div className="global-search">
          <Search size={14} />
          <input
            type="text"
            value={globalSearch}
            onChange={(e) => setGlobalSearch(e.target.value)}
            placeholder="Search companies, topics or questions"
            aria-label="Global search"
          />
        </div>
        <Link to="/companies" className="primary-button small-button">
          Explore Companies
        </Link>
      </div>
    </div>
  </header>
)

export default Header

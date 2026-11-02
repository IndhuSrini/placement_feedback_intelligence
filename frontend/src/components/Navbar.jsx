import { useState, useEffect } from "react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";
import {
  BarChart3,
  Building2,
  Home,
  Info,
  LogIn,
  LogOut,
  Menu,
  X,
  Sparkles,
} from "lucide-react";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const [mobileOpen, setMobileOpen] = useState(false);
  const token = localStorage.getItem("admin_token");
  const username = localStorage.getItem("admin_username") || "Admin";

  // Auto-close mobile menu on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  function handleLogout() {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_username");
    setMobileOpen(false);
    navigate("/");
  }

  return (
    <header className="navbar">
      <div className="nav-container">
        {/* Brand */}
        <NavLink to="/" className="brand" aria-label="Placement Intelligence Home">
          <div className="brand-icon">
            <BarChart3 size={22} strokeWidth={2.4} />
          </div>

          <div>
            <div className="brand-name">
              Placement Intelligence
            </div>
            <div className="brand-subtitle">
              Feedback Analytics Portal
            </div>
          </div>
        </NavLink>

        {/* Desktop Navigation */}
        <nav className="nav-links desktop-only" aria-label="Main Navigation">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            <Home size={16} />
            <span>Home</span>
          </NavLink>

          <NavLink
            to="/analytics"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            <BarChart3 size={16} />
            <span>Analytics</span>
          </NavLink>

          <NavLink
            to="/companies"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            <Building2 size={16} />
            <span>Companies</span>
          </NavLink>

          <NavLink
            to="/about"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            <Info size={16} />
            <span>About</span>
          </NavLink>

          {/* Auth Button */}
          {!token ? (
            <NavLink
              to="/login"
              className={({ isActive }) =>
                isActive
                  ? "nav-link nav-auth-btn active"
                  : "nav-link nav-auth-btn"
              }
            >
              <LogIn size={16} />
              <span>Admin Login</span>
            </NavLink>
          ) : (
            <div className="nav-logged-in-group">
              <span className="nav-user-badge" title={`Signed in as ${username}`}>
                <Sparkles size={13} />
                <span>{username}</span>
              </span>

              <button
                type="button"
                onClick={handleLogout}
                className="nav-link nav-logout-btn"
                title="Log out of admin session"
              >
                <LogOut size={16} />
                <span>Logout</span>
              </button>
            </div>
          )}
        </nav>

        {/* Mobile Hamburger Toggle */}
        <button
          type="button"
          className="mobile-nav-toggle mobile-only"
          onClick={() => setMobileOpen((prev) => !prev)}
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileOpen}
        >
          {mobileOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="mobile-menu mobile-only">
          <nav className="mobile-nav-links">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                isActive ? "mobile-nav-link active" : "mobile-nav-link"
              }
            >
              <Home size={18} />
              <span>Home</span>
            </NavLink>

            <NavLink
              to="/analytics"
              className={({ isActive }) =>
                isActive ? "mobile-nav-link active" : "mobile-nav-link"
              }
            >
              <BarChart3 size={18} />
              <span>Analytics Dashboard</span>
            </NavLink>

            <NavLink
              to="/companies"
              className={({ isActive }) =>
                isActive ? "mobile-nav-link active" : "mobile-nav-link"
              }
            >
              <Building2 size={18} />
              <span>Companies Directory</span>
            </NavLink>

            <NavLink
              to="/about"
              className={({ isActive }) =>
                isActive ? "mobile-nav-link active" : "mobile-nav-link"
              }
            >
              <Info size={18} />
              <span>About Project</span>
            </NavLink>

            <div className="mobile-menu-divider" />

            {!token ? (
              <NavLink
                to="/login"
                className="mobile-nav-link mobile-auth-btn"
              >
                <LogIn size={18} />
                <span>Admin Login</span>
              </NavLink>
            ) : (
              <button
                type="button"
                onClick={handleLogout}
                className="mobile-nav-link mobile-logout-btn"
              >
                <LogOut size={18} />
                <span>Logout ({username})</span>
              </button>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}


import {
  BrowserRouter,
  Routes,
  Route,
  NavLink,
  Navigate,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  BarChart3,
  Building2,
  Home,
  Info,
  LogIn,
  LogOut,
} from "lucide-react";

import HomePage from "./pages/Home";
import About from "./pages/About";
import Analytics from "./pages/Analytics";
import Companies from "./pages/Companies";
import CompanyDetails from "./pages/CompanyDetails";
import Login from "./pages/LoginPage";


function ProtectedRoute({ children }) {
  const token = localStorage.getItem("admin_token");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}


function Navigation() {
  const navigate = useNavigate();

  const token = localStorage.getItem("admin_token");
  const username = localStorage.getItem("admin_username");


  function handleLogout() {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_username");

    navigate("/");
  }


  return (
    <header className="navbar">

      <div className="nav-container">

        {/* Brand */}
        <NavLink to="/" className="brand">

          <div className="brand-icon">
            <BarChart3 size={21} />
          </div>

          <div>
            <div className="brand-name">
              Placement Intelligence
            </div>

            <div className="brand-subtitle">
              Feedback Analytics
            </div>
          </div>

        </NavLink>


        {/* Navigation */}
        <nav className="nav-links">

          {/* Home */}
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive
                ? "nav-link active"
                : "nav-link"
            }
          >
            <Home size={16} />
            <span>Home</span>
          </NavLink>


          {/* Analytics */}
          <NavLink
            to="/analytics"
            className={({ isActive }) =>
              isActive
                ? "nav-link active"
                : "nav-link"
            }
          >
            <BarChart3 size={16} />
            <span>Analytics</span>
          </NavLink>


          {/* Companies */}
          <NavLink
            to="/companies"
            className={({ isActive }) =>
              isActive
                ? "nav-link active"
                : "nav-link"
            }
          >
            <Building2 size={16} />
            <span>Companies</span>
          </NavLink>


          {/* About */}
          <NavLink
            to="/about"
            className={({ isActive }) =>
              isActive
                ? "nav-link active"
                : "nav-link"
            }
          >
            <Info size={16} />
            <span>About</span>
          </NavLink>


          {/* Login / Logout */}
          {!token ? (

            <NavLink
              to="/login"
              className={({ isActive }) =>
                isActive
                  ? "nav-link active"
                  : "nav-link"
              }
            >
              <LogIn size={16} />
              <span>Admin Login</span>
            </NavLink>

          ) : (

            <button
              type="button"
              onClick={handleLogout}
              className="nav-link"
              style={{
                border: "none",
                background: "transparent",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                font: "inherit",
              }}
              title={`Logged in as ${username || "admin"}`}
            >
              <LogOut size={16} />
              <span>Logout</span>
            </button>

          )}

        </nav>

      </div>

    </header>
  );
}


function AppContent() {

  const location = useLocation();

  const isLoginPage =
    location.pathname === "/login";


  return (
    <>

      {/* Hide navbar on login page */}
      {!isLoginPage && <Navigation />}


      <Routes>

        {/* ==============================
            PUBLIC PAGES
           ============================== */}

        <Route
          path="/"
          element={<HomePage />}
        />

        <Route
          path="/about"
          element={<About />}
        />


        {/* ==============================
            LOGIN
           ============================== */}

        <Route
          path="/login"
          element={<Login />}
        />


        {/* ==============================
            PROTECTED PAGES
           ============================== */}

        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <Analytics />
            </ProtectedRoute>
          }
        />


        <Route
          path="/companies"
          element={
            <ProtectedRoute>
              <Companies />
            </ProtectedRoute>
          }
        />


        <Route
          path="/companies/:companyId"
          element={
            <ProtectedRoute>
              <CompanyDetails />
            </ProtectedRoute>
          }
        />

      </Routes>

    </>
  );
}


function App() {

  return (
    <BrowserRouter>

      <AppContent />

    </BrowserRouter>
  );
}


export default App;

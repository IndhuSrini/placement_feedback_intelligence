import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";

import HomePage from "./pages/Home";
import About from "./pages/About";
import Analytics from "./pages/Analytics";
import Companies from "./pages/Companies";
import CompanyDetails from "./pages/CompanyDetails";
import Login from "./pages/LoginPage";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import PlacementAssistant from "./components/PlacementAssistant";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("admin_token");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function AppContent() {
  const location = useLocation();
  const isLoginPage = location.pathname === "/login";

  return (
    <div className="app-layout">
      {/* Hide navbar on login page */}
      {!isLoginPage && <Navbar />}

      <div className="main-content-area">
        <Routes>
          {/* ==============================
              PUBLIC PAGES
             ============================== */}
          <Route path="/" element={<HomePage />} />
          <Route path="/about" element={<About />} />

          {/* ==============================
              LOGIN
             ============================== */}
          <Route path="/login" element={<Login />} />

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

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>

      {/* Hide footer on login page */}
      {!isLoginPage && <Footer />}

      {!isLoginPage && localStorage.getItem("admin_token") && (
        <PlacementAssistant />
      )}
    </div>
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

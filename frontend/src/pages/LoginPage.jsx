
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BarChart3,
  LockKeyhole,
  User,
  Eye,
  EyeOff,
  ShieldCheck,
  ArrowRight,
} from "lucide-react";


export default function Login() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);


  async function handleLogin(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Invalid username or password"
        );
      }

      localStorage.setItem(
        "admin_token",
        data.access_token
      );

      localStorage.setItem(
        "admin_username",
        data.username
      );

      navigate("/analytics");

    } catch (err) {
      setError(
        err.message || "Unable to login. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <div className="login-page">

      {/* Background decoration */}
      <div className="login-background-shape shape-one"></div>
      <div className="login-background-shape shape-two"></div>


      <div className="login-container">

        {/* Left branding section */}
        <div className="login-brand-section">

          <div className="login-brand-icon">
            <BarChart3 size={32} strokeWidth={2} />
          </div>

          <h1>
            Placement
            <br />
            Intelligence
          </h1>

          <p>
            Feedback Analytics Portal
          </p>


          <div className="login-brand-divider"></div>


          <div className="login-feature">
            <div className="login-feature-icon">
              <ShieldCheck size={20} />
            </div>

            <div>
              <strong>Secure Admin Access</strong>
              <span>
                Access placement insights and analytics
              </span>
            </div>
          </div>


          <div className="login-feature">
            <div className="login-feature-icon">
              <BarChart3 size={20} />
            </div>

            <div>
              <strong>Placement Analytics</strong>
              <span>
                Explore company and recruitment insights
              </span>
            </div>
          </div>

        </div>


        {/* Login form section */}
        <div className="login-form-section">

          <div className="login-form-header">

            <div className="login-mobile-icon">
              <BarChart3 size={24} />
            </div>

            <h2>
              Welcome back
            </h2>

            <p>
              Sign in to access the admin dashboard
            </p>

          </div>


          <form onSubmit={handleLogin}>

            {/* Username */}
            <div className="login-input-group">

              <label htmlFor="username">
                Username
              </label>

              <div className="login-input-wrapper">

                <User
                  size={19}
                  className="login-input-icon"
                />

                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) =>
                    setUsername(e.target.value)
                  }
                  placeholder="Enter your username"
                  autoComplete="username"
                  required
                />

              </div>

            </div>


            {/* Password */}
            <div className="login-input-group">

              <label htmlFor="password">
                Password
              </label>

              <div className="login-input-wrapper">

                <LockKeyhole
                  size={19}
                  className="login-input-icon"
                />

                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) =>
                    setPassword(e.target.value)
                  }
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(!showPassword)
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}
                </button>

              </div>

            </div>


            {/* Error */}
            {error && (
              <div className="login-error">
                <span>!</span>
                <p>{error}</p>
              </div>
            )}


            {/* Login button */}
            <button
              type="submit"
              className="login-submit"
              disabled={loading}
            >

              {loading ? (
                <>
                  <span className="login-spinner"></span>
                  Signing in...
                </>
              ) : (
                <>
                  Sign in
                  <ArrowRight size={18} />
                </>
              )}

            </button>

          </form>


          <div className="login-footer">

            <ShieldCheck size={15} />

            <span>
              Authorized administrator access only
            </span>

          </div>

        </div>

      </div>

    </div>
  );
}


import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { loginAdmin } from "../services/api";

function AdminLogin({ onLogin }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("Admin123!");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const data = await loginAdmin(username, password);
      onLogin(data.admin);
      navigate(location.state?.from || "/admin", { replace: true });
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="eyebrow">Admin Login</p>
        <h1>Sign in to CookieBot Admin</h1>
        <p>
          Admin pages are protected. Sign in before managing orders, products,
          dashboard data, and chat sessions.
        </p>

        <form className="admin-form" onSubmit={handleSubmit}>
          <label>
            Username or email
            <input
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="admin"
              autoComplete="username"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Admin password"
              autoComplete="current-password"
            />
          </label>

          {error && <p className="error-text">{error}</p>}

          <button type="submit" disabled={isLoading}>
            {isLoading ? "Signing in..." : "Login"}
          </button>
        </form>

        <div className="demo-credentials">
          <strong>Default local admin</strong>
          <span>Username: admin</span>
          <span>Password: Admin123!</span>
        </div>

        <Link to="/" className="back-link">
          Back to home
        </Link>
      </section>
    </main>
  );
}

export default AdminLogin;

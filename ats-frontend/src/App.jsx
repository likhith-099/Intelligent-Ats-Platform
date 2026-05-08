import { useEffect, useState } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import Login from "./pages/login";
import Register from "./pages/register";
import Dashboard from "./pages/dashboard";
import CreateJob from "./pages/createjob";
import UploadResume from "./pages/uploadresume";
import RankResume from "./pages/rankresume";
import Jobs from "./pages/jobs";
import ProtectedLayout from "./components/ProtectedLayout";
import "./App.css";

const platformHighlights = [
  {
    title: "Smart Parsing",
    description: "Turn resumes into structured candidate profiles in seconds.",
  },
  {
    title: "Instant Ranking",
    description:
      "Compare every resume against each job and surface top matches.",
  },
  {
    title: "Hiring Focus",
    description:
      "Keep recruiters aligned with one clear, searchable hiring workspace.",
  },
];

function AuthLanding() {
  const [authMode, setAuthMode] = useState("login");
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      navigate("/dashboard", { replace: true });
    }
  }, [navigate]);

  const onLoginSuccess = () => {
    navigate("/dashboard", { replace: true });
  };

  return (
    <div className="app-shell">
      <div className="ambient ambient-one" aria-hidden="true" />
      <div className="ambient ambient-two" aria-hidden="true" />

      <main className="landing">
        <section className="intro-panel">
          <p className="eyebrow">AI Recruiting Workspace</p>
          <h1>Intelligent ATS Platform</h1>
          <p className="intro-copy">
            Evaluate resumes faster, keep hiring decisions consistent, and move
            the best candidates forward with confidence.
          </p>

          <div className="feature-grid">
            {platformHighlights.map((item) => (
              <article className="feature-card" key={item.title}>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="auth-panel">
          <div className="auth-stack">
            <div className="auth-toggle" role="tablist" aria-label="Authentication options">
              <button
                type="button"
                role="tab"
                aria-selected={authMode === "login"}
                className={`auth-tab ${authMode === "login" ? "active" : ""}`}
                onClick={() => setAuthMode("login")}
              >
                Login
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={authMode === "register"}
                className={`auth-tab ${authMode === "register" ? "active" : ""}`}
                onClick={() => setAuthMode("register")}
              >
                Register
              </button>
            </div>

            {authMode === "login" ? (
              <Login
                onSwitchToRegister={() => setAuthMode("register")}
                onLoginSuccess={onLoginSuccess}
              />
            ) : (
              <Register onSwitchToLogin={() => setAuthMode("login")} />
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<AuthLanding />} />
      <Route element={<ProtectedLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/create-job" element={<CreateJob />} />
        <Route path="/upload-resume" element={<UploadResume />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/rank-resume" element={<RankResume />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;

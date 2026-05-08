import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import API from "../api/api";

function ProtectedLayout() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/", { replace: true });
      return;
    }

    const loadUser = async () => {
      try {
        const res = await API.get("/me");
        setUser(res.data);
      } catch {
        localStorage.removeItem("token");
        navigate("/", { replace: true });
      }
    };

    loadUser();
  }, [navigate]);

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/", { replace: true });
  };

  const navItems =
    user?.role === "recruiter"
      ? [
          { to: "/dashboard", label: "Dashboard" },
          { to: "/create-job", label: "Create Job" },
          { to: "/rank-resume", label: "Rank Applicants" },
        ]
      : [
          { to: "/dashboard", label: "Dashboard" },
          { to: "/upload-resume", label: "My Resumes" },
          { to: "/jobs", label: "Find Jobs" },
        ];

  if (!user) {
    return (
      <div className="page-shell">
        <div className="page-card page-center">
          <h2>Loading workspace...</h2>
          <p>Verifying your session.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-shell">
      <header className="topbar">
        <div>
          <p className="topbar-eyebrow">ATS Workspace</p>
          <h1 className="topbar-title">Intelligent ATS Platform</h1>
        </div>

        <div className="topbar-meta">
          <div className="user-chip">
            <span>{user.email}</span>
            <strong>{user.role}</strong>
          </div>
          <button className="ghost-button" type="button" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      <nav className="route-nav">
        {navItems.map((item) => (
          <NavLink key={item.to} to={item.to} className="route-link">
            {item.label}
          </NavLink>
        ))}
      </nav>

      <main className="workspace">
        <Outlet context={{ user }} />
      </main>
    </div>
  );
}

export default ProtectedLayout;

import { useState } from "react";
import API from "../api/api";
import getApiErrorMessage from "../api/getApiErrorMessage";

function Login({ onSwitchToRegister, onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState({ type: "idle", message: "" });

  const login = async (event) => {
    event.preventDefault();

    if (!email || !password) {
      setStatus({
        type: "error",
        message: "Enter both email and password to continue.",
      });
      return;
    }

    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);

    try {
      setStatus({ type: "loading", message: "Signing you in..." });
      const res = await API.post("/login", form);
      localStorage.setItem("token", res.data.access_token);
      setStatus({
        type: "success",
        message: "Login successful. Your session is ready.",
      });
      if (onLoginSuccess) {
        onLoginSuccess();
      }
    } catch (error) {
      const message = getApiErrorMessage(
        error,
        "Unable to login right now. Please try again.",
      );
      setStatus({ type: "error", message });
    }
  };

  return (
    <form className="login-card" onSubmit={login}>
      <div className="login-header">
        <p className="login-kicker">Welcome back</p>
        <h2>Sign in to continue</h2>
        <p>Access jobs, candidate rankings, and resume uploads in one place.</p>
      </div>

      <label className="input-group" htmlFor="email">
        <span>Email</span>
        <input
          id="email"
          type="email"
          placeholder="you@company.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          required
        />
      </label>

      <label className="input-group" htmlFor="password">
        <span>Password</span>
        <input
          id="password"
          type="password"
          placeholder="Enter your password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
      </label>

      <button className="primary-button" type="submit" disabled={status.type === "loading"}>
        {status.type === "loading" ? "Signing in..." : "Login"}
      </button>

      {status.message ? (
        <p className={`status-message ${status.type}`}>{status.message}</p>
      ) : null}

      <p className="form-switch-row">
        <span>New here?</span>
        <button className="text-button" type="button" onClick={onSwitchToRegister}>
          Create account
        </button>
      </p>
    </form>
  );
}

export default Login;

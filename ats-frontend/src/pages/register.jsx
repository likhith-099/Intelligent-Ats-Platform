import { useState } from "react";
import API from "../api/api";
import getApiErrorMessage from "../api/getApiErrorMessage";

function Register({ onSwitchToLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("candidate");
  const [status, setStatus] = useState({ type: "idle", message: "" });

  const register = async (event) => {
    event.preventDefault();

    if (!email || !password || !role) {
      setStatus({
        type: "error",
        message: "Fill in all fields to create your account.",
      });
      return;
    }

    try {
      setStatus({ type: "loading", message: "Creating your account..." });
      await API.post("/register", {
        email,
        password,
        role,
      });

      setStatus({
        type: "success",
        message: "Registration successful. Please login to continue.",
      });
      setPassword("");
    } catch (error) {
      const message = getApiErrorMessage(
        error,
        "Unable to register right now. Please try again.",
      );
      setStatus({ type: "error", message });
    }
  };

  return (
    <form className="login-card" onSubmit={register}>
      <div className="login-header">
        <p className="login-kicker">Get started</p>
        <h2>Create your account</h2>
        <p>Choose your role and start using the ATS workspace.</p>
      </div>

      <label className="input-group" htmlFor="register-email">
        <span>Email</span>
        <input
          id="register-email"
          type="email"
          placeholder="you@company.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          required
        />
      </label>

      <label className="input-group" htmlFor="register-password">
        <span>Password</span>
        <input
          id="register-password"
          type="password"
          placeholder="Create a secure password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
          required
        />
      </label>

      <label className="input-group" htmlFor="register-role">
        <span>Role</span>
        <select
          id="register-role"
          value={role}
          onChange={(e) => setRole(e.target.value)}
        >
          <option value="candidate">Candidate</option>
          <option value="recruiter">Recruiter</option>
        </select>
      </label>

      <button className="primary-button" type="submit" disabled={status.type === "loading"}>
        {status.type === "loading" ? "Creating account..." : "Register"}
      </button>

      {status.message ? (
        <p className={`status-message ${status.type}`}>{status.message}</p>
      ) : null}

      <p className="form-switch-row">
        <span>Already registered?</span>
        <button className="text-button" type="button" onClick={onSwitchToLogin}>
          Back to login
        </button>
      </p>
    </form>
  );
}

export default Register;

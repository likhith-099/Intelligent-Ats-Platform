import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import API from "../api/api";
import getApiErrorMessage from "../api/getApiErrorMessage";

function RankResume() {
  const { user } = useOutletContext();
  const [jobId, setJobId] = useState("");
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [status, setStatus] = useState({ type: "idle", message: "" });
  const [results, setResults] = useState([]);
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    const loadJobs = async () => {
      try {
        const res = await API.get("/jobs");
        const loadedJobs = res.data || [];
        setJobs(loadedJobs);
        setJobId((current) => current || String(loadedJobs[0]?.id || ""));
      } catch (error) {
        setStatus({
          type: "error",
          message: getApiErrorMessage(error, "Unable to load jobs right now."),
        });
      }
    };

    if (user.role === "recruiter") {
      loadJobs();
    }
  }, [user.role]);

  if (user.role !== "recruiter") {
    return (
      <section className="page-card">
        <div className="page-title-row">
          <h2>Recruiter Area</h2>
          <p>Only recruiters can rank applicants.</p>
        </div>
      </section>
    );
  }

  const runRanking = async (event) => {
    event.preventDefault();

    if (!jobId) {
      setStatus({ type: "error", message: "Enter a job ID to rank applicants." });
      return;
    }

    try {
      setStatus({ type: "loading", message: "Ranking applicants..." });
      const res = await API.post(`/rank-applicants/${jobId}`, null, {
        params: { page, limit },
      });

      setResults(res.data.results || []);
      setStatus({
        type: "success",
        message: `Loaded ${res.data.results?.length || 0} of ${res.data.total_applicants || 0} applicants.`,
      });
    } catch (error) {
      setResults([]);
      setStatus({
        type: "error",
        message: getApiErrorMessage(error, "Unable to rank applicants right now."),
      });
    }
  };

  return (
    <section className="page-card">
      <div className="page-title-row">
        <h2>Rank Applicants</h2>
        <p>Select one of your jobs to generate ranked candidate results.</p>
      </div>

      <form className="tool-form compact-grid" onSubmit={runRanking}>
        <label className="input-group" htmlFor="job-id">
          <span>Job</span>
          <select
            id="job-id"
            value={jobId}
            onChange={(e) => setJobId(e.target.value)}
            required
          >
            <option value="">Choose a job</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title} (ID {job.id})
              </option>
            ))}
          </select>
        </label>

        <label className="input-group" htmlFor="rank-page">
          <span>Page</span>
          <input
            id="rank-page"
            type="number"
            min="1"
            value={page}
            onChange={(e) => setPage(Number(e.target.value))}
          />
        </label>

        <label className="input-group" htmlFor="rank-limit">
          <span>Limit</span>
          <input
            id="rank-limit"
            type="number"
            min="1"
            max="50"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
          />
        </label>

        <button className="primary-button" type="submit" disabled={status.type === "loading"}>
          {status.type === "loading" ? "Ranking..." : "Run Ranking"}
        </button>
      </form>

      {status.message ? (
        <p className={`status-message ${status.type}`}>{status.message}</p>
      ) : null}

      {results.length > 0 ? (
        <div className="table-wrap">
          <table className="result-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Resume</th>
                <th>Semantic</th>
                <th>Skill</th>
                <th>Overall</th>
              </tr>
            </thead>
            <tbody>
              {results.map((row) => (
                <tr key={row.resume_id}>
                  <td>{row.rank}</td>
                  <td>{row.filename}</td>
                  <td>{row.semantic_score}</td>
                  <td>{row.skill_alignment}</td>
                  <td>{row.overall_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {jobs.length === 0 && status.type !== "loading" ? (
        <p className="empty-state">Create a job before ranking applicants.</p>
      ) : null}
    </section>
  );
}

export default RankResume;

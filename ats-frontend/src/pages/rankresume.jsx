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
  const [expandedRow, setExpandedRow] = useState(null);

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
      setExpandedRow(null);
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

  const toggleExpand = (resumeId) => {
    setExpandedRow(expandedRow === resumeId ? null : resumeId);
  };

  const getScoreClass = (score) => {
    if (score >= 70) return "score-high";
    if (score >= 40) return "score-medium";
    return "score-low";
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
          <table className="result-table ranking-table">
            <thead>
              <tr>
                <th style={{ width: "50px" }}>#</th>
                <th>Applicant</th>
                <th>Resume</th>
                <th>Semantic</th>
                <th>Keywords</th>
                <th>Content</th>
                <th>Overall</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {results.map((row) => (
                <>
                  <tr key={row.resume_id} className={expandedRow === row.resume_id ? "row-expanded" : ""}>
                    <td className="rank-cell">{row.rank}</td>
                    <td className="applicant-cell">
                      <div className="applicant-name">{row.applicant_name}</div>
                      <div className="applicant-email">{row.applicant_email}</div>
                    </td>
                    <td>{row.filename}</td>
                    <td className={getScoreClass(row.semantic_score)}>{row.semantic_score}%</td>
                    <td className={getScoreClass(row.keyword_score)}>{row.keyword_score}%</td>
                    <td className={getScoreClass(row.content_density)}>{row.content_density}%</td>
                    <td className={`overall-score ${getScoreClass(row.overall_score)}`}>
                      <strong>{row.overall_score}%</strong>
                    </td>
                    <td>
                      <button
                        className="expand-btn"
                        onClick={() => toggleExpand(row.resume_id)}
                      >
                        {expandedRow === row.resume_id ? "−" : "+"}
                      </button>
                    </td>
                  </tr>
                  {expandedRow === row.resume_id && (
                    <tr key={`${row.resume_id}-details`} className="details-row">
                      <td colSpan={8}>
                        <div className="details-content">
                          <div className="details-grid">
                            <div className="detail-item">
                              <span className="detail-label">Education</span>
                              <span className={`detail-value ${row.has_education ? "present" : "missing"}`}>
                                {row.has_education ? "✓ Found" : "✗ Not found"}
                              </span>
                            </div>
                            <div className="detail-item">
                              <span className="detail-label">Experience</span>
                              <span className={`detail-value ${row.has_experience ? "present" : "missing"}`}>
                                {row.has_experience ? "✓ Found" : "✗ Not found"}
                              </span>
                            </div>
                            <div className="detail-item">
                              <span className="detail-label">Applied</span>
                              <span className="detail-value">{row.applied_at ? new Date(row.applied_at).toLocaleDateString() : "N/A"}</span>
                            </div>
                          </div>
                          {row.matched_keywords?.length > 0 && (
                            <div className="keyword-section">
                              <span className="detail-label">Matched Keywords:</span>
                              <div className="keyword-tags matched">
                                {row.matched_keywords.map((kw, i) => (
                                  <span key={i} className="keyword-tag">{kw}</span>
                                ))}
                              </div>
                            </div>
                          )}
                          {row.missing_keywords?.length > 0 && (
                            <div className="keyword-section">
                              <span className="detail-label">Missing Keywords:</span>
                              <div className="keyword-tags missing">
                                {row.missing_keywords.map((kw, i) => (
                                  <span key={i} className="keyword-tag">{kw}</span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
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

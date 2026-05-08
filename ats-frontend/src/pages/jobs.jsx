import { useEffect, useMemo, useState } from "react";
import { useOutletContext } from "react-router-dom";
import API from "../api/api";
import getApiErrorMessage from "../api/getApiErrorMessage";

function Jobs() {
  const { user } = useOutletContext();
  const [jobs, setJobs] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [applications, setApplications] = useState([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [status, setStatus] = useState({ type: "idle", message: "" });
  const [applyingJobId, setApplyingJobId] = useState(null);

  const appliedJobIds = useMemo(
    () => new Set(applications.map((application) => application.job_id)),
    [applications],
  );

  const loadCandidateData = async () => {
    try {
      setStatus({ type: "loading", message: "Loading jobs..." });
      const [jobsRes, resumesRes, applicationsRes] = await Promise.all([
        API.get("/jobs"),
        API.get("/my-resumes"),
        API.get("/my-applications"),
      ]);

      const loadedResumes = resumesRes.data || [];
      setJobs(jobsRes.data || []);
      setResumes(loadedResumes);
      setApplications(applicationsRes.data || []);
      setSelectedResumeId((current) => current || String(loadedResumes[0]?.id || ""));
      setStatus({ type: "idle", message: "" });
    } catch (error) {
      setStatus({
        type: "error",
        message: getApiErrorMessage(error, "Unable to load candidate workspace."),
      });
    }
  };

  useEffect(() => {
    if (user.role === "candidate") {
      loadCandidateData();
    }
  }, [user.role]);

  const applyToJob = async (jobId) => {
    if (!selectedResumeId) {
      setStatus({ type: "error", message: "Upload or select a resume before applying." });
      return;
    }

    try {
      setApplyingJobId(jobId);
      setStatus({ type: "loading", message: "Submitting application..." });
      await API.post(`/apply/${jobId}/${selectedResumeId}`);
      await loadCandidateData();
      setStatus({ type: "success", message: "Application submitted successfully." });
    } catch (error) {
      setStatus({
        type: "error",
        message: getApiErrorMessage(error, "Unable to submit application."),
      });
    } finally {
      setApplyingJobId(null);
    }
  };

  if (user.role !== "candidate") {
    return (
      <section className="page-card">
        <div className="page-title-row">
          <h2>Candidate Area</h2>
          <p>Only candidates can browse and apply to jobs.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="page-card">
      <div className="page-title-row">
        <h2>Find Jobs</h2>
        <p>Choose a resume, browse available roles, and submit applications.</p>
      </div>

      <div className="resume-picker">
        <label className="input-group" htmlFor="resume-select">
          <span>Apply with resume</span>
          <select
            id="resume-select"
            value={selectedResumeId}
            onChange={(event) => setSelectedResumeId(event.target.value)}
            disabled={resumes.length === 0}
          >
            {resumes.length === 0 ? (
              <option value="">Upload a resume first</option>
            ) : (
              resumes.map((resume) => (
                <option key={resume.id} value={resume.id}>
                  {resume.original_filename || resume.filename}
                </option>
              ))
            )}
          </select>
        </label>
      </div>

      {status.message ? (
        <p className={`status-message ${status.type}`}>{status.message}</p>
      ) : null}

      <div className="job-list">
        {jobs.length > 0 ? (
          jobs.map((job) => {
            const applied = appliedJobIds.has(job.id);
            return (
              <article className="job-card" key={job.id}>
                <div>
                  <h3>{job.title}</h3>
                  <span>Job ID {job.id}</span>
                </div>
                <p>{job.description}</p>
                <button
                  className={applied ? "secondary-button" : "primary-button"}
                  type="button"
                  disabled={applied || applyingJobId === job.id || resumes.length === 0}
                  onClick={() => applyToJob(job.id)}
                >
                  {applied ? "Applied" : applyingJobId === job.id ? "Applying..." : "Apply"}
                </button>
              </article>
            );
          })
        ) : (
          <p className="empty-state">No jobs are available yet.</p>
        )}
      </div>
    </section>
  );
}

export default Jobs;

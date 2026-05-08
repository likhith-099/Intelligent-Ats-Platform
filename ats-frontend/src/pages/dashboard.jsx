import { useEffect, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";
import API from "../api/api";
import getApiErrorMessage from "../api/getApiErrorMessage";

function Dashboard() {
  const { user } = useOutletContext();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [jobs, setJobs] = useState([]);
  const [editingJobId, setEditingJobId] = useState(null);
  const [status, setStatus] = useState({ type: "idle", message: "" });
  const [isSaving, setIsSaving] = useState(false);
  const [deletingJobId, setDeletingJobId] = useState(null);

  const cards =
    user.role === "recruiter"
      ? [
          {
            title: "Rank Applicants",
            description: "Pick one of your jobs and score submitted resumes.",
            to: "/rank-resume",
            action: "Start Ranking",
          },
        ]
      : [
          {
            title: "Upload Resume",
            description: "Add your latest resume PDF for job matching.",
            to: "/upload-resume",
            action: "Upload Now",
          },
          {
            title: "Find Jobs",
            description: "Browse open jobs and apply with an uploaded resume.",
            to: "/jobs",
            action: "View Jobs",
          },
        ];

  useEffect(() => {
    let isMounted = true;

    const loadJobs = async () => {
      if (user.role !== "recruiter") {
        return;
      }

      try {
        const res = await API.get("/jobs");
        if (isMounted) {
          setJobs(res.data || []);
        }
      } catch {
        if (isMounted) {
          setJobs([]);
        }
      }
    };

    loadJobs();

    return () => {
      isMounted = false;
    };
  }, [user.role]);

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setEditingJobId(null);
  };

  const refreshJobs = async () => {
    const res = await API.get("/jobs");
    setJobs(res.data || []);
  };

  const submitJob = async (event) => {
    event.preventDefault();

    if (!editingJobId) {
      return;
    }

    if (!title.trim() || !description.trim()) {
      setStatus({ type: "error", message: "Add both title and description." });
      return;
    }

    try {
      setIsSaving(true);
      setStatus({ type: "loading", message: "Updating job..." });
      await API.put(`/jobs/${editingJobId}`, {
        title,
        description,
      });
      setStatus({ type: "success", message: "Job updated successfully." });

      resetForm();
      await refreshJobs();
    } catch (error) {
      setStatus({
        type: "error",
        message: getApiErrorMessage(error, "Unable to save job right now."),
      });
    } finally {
      setIsSaving(false);
    }
  };

  const startEdit = (job) => {
    setTitle(job.title);
    setDescription(job.description);
    setEditingJobId(job.id);
    setStatus({ type: "idle", message: "" });
  };

  const removeJob = async (jobId) => {
    try {
      setDeletingJobId(jobId);
      setStatus({ type: "loading", message: "Deleting job..." });
      await API.delete(`/jobs/${jobId}`);

      if (editingJobId === jobId) {
        resetForm();
      }

      await refreshJobs();
      setStatus({ type: "success", message: "Job deleted successfully." });
    } catch (error) {
      setStatus({
        type: "error",
        message: getApiErrorMessage(error, "Unable to delete this job right now."),
      });
    } finally {
      setDeletingJobId(null);
    }
  };

  return (
    <section className="page-card">
      <div className="page-title-row">
        <h2>{user.role === "recruiter" ? "Recruiter Dashboard" : "Candidate Dashboard"}</h2>
        <p>Choose the next step for your workspace.</p>
      </div>

      <div className="task-grid">
        {cards.map((card) => (
          <article key={card.title} className="task-card">
            <h3>{card.title}</h3>
            <p>{card.description}</p>
            <Link to={card.to} className="inline-link">
              {card.action}
            </Link>
          </article>
        ))}
      </div>

      {user.role === "recruiter" ? (
        <>
          {editingJobId ? (
            <form className="tool-form" onSubmit={submitJob}>
              <label className="input-group" htmlFor="dashboard-job-title">
                <span>Job Title</span>
                <input
                  id="dashboard-job-title"
                  placeholder="Frontend Engineer"
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  required
                />
              </label>

              <label className="input-group" htmlFor="dashboard-job-description">
                <span>Description</span>
                <textarea
                  id="dashboard-job-description"
                  placeholder="Role responsibilities, required skills, and experience..."
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  rows={8}
                  required
                />
              </label>

              <button className="primary-button" type="submit" disabled={isSaving}>
                {isSaving ? "Updating..." : "Update Job"}
              </button>
              <button className="secondary-button" type="button" onClick={resetForm}>
                Cancel Edit
              </button>
            </form>
          ) : null}

          <div className="list-panel">
            <h3>Your Jobs</h3>
            <div className="item-list">
              {jobs.length > 0 ? (
                jobs.map((job) => (
                  <article className="list-item" key={job.id}>
                    <div>
                      <strong>{job.title}</strong>
                      <span>Job ID {job.id}</span>
                    </div>
                    <p>{job.description}</p>
                    <div className="job-actions">
                      <button
                        className="secondary-button"
                        type="button"
                        onClick={() => startEdit(job)}
                        disabled={isSaving || deletingJobId === job.id}
                      >
                        Edit
                      </button>
                      <button
                        className="ghost-button"
                        type="button"
                        onClick={() => removeJob(job.id)}
                        disabled={deletingJobId === job.id}
                      >
                        {deletingJobId === job.id ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                  </article>
                ))
              ) : (
                <p className="empty-state">No jobs created yet.</p>
              )}
            </div>
          </div>

          {status.message ? (
            <p className={`status-message ${status.type}`}>{status.message}</p>
          ) : null}
        </>
      ) : null}
    </section>
  );
}

export default Dashboard;

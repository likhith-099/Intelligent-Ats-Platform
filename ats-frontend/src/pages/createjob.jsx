import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import API from "../api/api";
import getApiErrorMessage from "../api/getApiErrorMessage";

function CreateJob() {
  const { user } = useOutletContext();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState({ type: "idle", message: "" });

  if (user.role !== "recruiter") {
    return (
      <section className="page-card">
        <div className="page-title-row">
          <h2>Recruiter Area</h2>
          <p>Only recruiters can create jobs.</p>
        </div>
      </section>
    );
  }

  const submitJob = async (event) => {
    event.preventDefault();

    if (!title || !description) {
      setStatus({
        type: "error",
        message: "Add both title and description.",
      });
      return;
    }

    try {
      setStatus({ type: "loading", message: "Creating job..." });
      const res = await API.post("/create-job", {
        title,
        description,
      });

      setStatus({
        type: "success",
        message: `Job created successfully (Job ID: ${res.data.job_id}).`,
      });
      setTitle("");
      setDescription("");
    } catch (error) {
      setStatus({
        type: "error",
        message: getApiErrorMessage(error, "Unable to create job right now."),
      });
    }
  };

  return (
    <section className="page-card">
      <div className="page-title-row">
        <h2>Create Job</h2>
        <p>Recruiters can create a job and then rank matching applicants.</p>
      </div>

      <form className="tool-form" onSubmit={submitJob}>
        <label className="input-group" htmlFor="job-title">
          <span>Job Title</span>
          <input
            id="job-title"
            placeholder="Frontend Engineer"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </label>

        <label className="input-group" htmlFor="job-description">
          <span>Description</span>
          <textarea
            id="job-description"
            placeholder="Role responsibilities, required skills, and experience..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={8}
            required
          />
        </label>

        <button className="primary-button" type="submit" disabled={status.type === "loading"}>
          {status.type === "loading" ? "Creating..." : "Create Job"}
        </button>

        {status.message ? (
          <p className={`status-message ${status.type}`}>{status.message}</p>
        ) : null}
      </form>
    </section>
  );
}

export default CreateJob;

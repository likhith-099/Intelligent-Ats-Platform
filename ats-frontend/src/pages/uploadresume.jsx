import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import API from "../api/api";
import getApiErrorMessage from "../api/getApiErrorMessage";

function UploadResume() {
  const { user } = useOutletContext();
  const [resumeFile, setResumeFile] = useState(null);
  const [status, setStatus] = useState({ type: "idle", message: "" });
  const [resumes, setResumes] = useState([]);

  useEffect(() => {
    let isMounted = true;

    const loadResumes = async () => {
      try {
        const res = await API.get("/my-resumes");
        if (isMounted) {
          setResumes(res.data || []);
        }
      } catch {
        if (isMounted) {
          setResumes([]);
        }
      }
    };

    if (user.role === "candidate") {
      loadResumes();
    }

    return () => {
      isMounted = false;
    };
  }, [user.role]);

  const refreshResumes = async () => {
    try {
      const res = await API.get("/my-resumes");
      setResumes(res.data || []);
    } catch {
      setResumes([]);
    }
  };

  if (user.role !== "candidate") {
    return (
      <section className="page-card">
        <div className="page-title-row">
          <h2>Candidate Area</h2>
          <p>Only candidates can upload resumes.</p>
        </div>
      </section>
    );
  }

  const upload = async (event) => {
    event.preventDefault();

    if (!resumeFile) {
      setStatus({
        type: "error",
        message: "Choose a PDF file before uploading.",
      });
      return;
    }

    const formData = new FormData();
    formData.append("file", resumeFile);

    try {
      setStatus({ type: "loading", message: "Uploading resume..." });
      const res = await API.post("/upload-resume", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus({
        type: "success",
        message: `Upload complete (Resume ID: ${res.data.resume_id}).`,
      });
      setResumeFile(null);
      event.target.reset();
      refreshResumes();
    } catch (error) {
      setStatus({
        type: "error",
        message: getApiErrorMessage(error, "Unable to upload resume right now."),
      });
    }
  };

  return (
    <section className="page-card">
      <div className="page-title-row">
        <h2>Upload Resume</h2>
        <p>Candidates can upload a PDF resume to participate in matching.</p>
      </div>

      <form className="tool-form" onSubmit={upload}>
        <label className="input-group" htmlFor="resume-file">
          <span>Resume PDF</span>
          <input
            id="resume-file"
            type="file"
            accept=".pdf,application/pdf"
            onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
            required
          />
        </label>

        <button className="primary-button" type="submit" disabled={status.type === "loading"}>
          {status.type === "loading" ? "Uploading..." : "Upload Resume"}
        </button>

        {status.message ? (
          <p className={`status-message ${status.type}`}>{status.message}</p>
        ) : null}
      </form>

      <div className="list-panel">
        <h3>Uploaded Resumes</h3>
        {resumes.length > 0 ? (
          <div className="item-list">
            {resumes.map((resume) => (
              <article className="list-item" key={resume.id}>
                <div>
                  <strong>{resume.original_filename || resume.filename}</strong>
                  <span>Resume ID {resume.id}</span>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-state">No resumes uploaded yet.</p>
        )}
      </div>
    </section>
  );
}

export default UploadResume;

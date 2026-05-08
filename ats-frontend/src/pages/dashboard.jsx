import { Link, useOutletContext } from "react-router-dom";

function Dashboard() {
  const { user } = useOutletContext();

  const cards =
    user.role === "recruiter"
      ? [
          {
            title: "Create a Job",
            description: "Post a role and store it for candidate matching.",
            to: "/create-job",
            action: "Open Job Form",
          },
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
    </section>
  );
}

export default Dashboard;

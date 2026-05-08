# Resume AI ATS Platform

An end-to-end AI-powered Applicant Tracking System (ATS) for modern hiring workflows.

This project helps recruiters and candidates collaborate in one platform:
- Recruiters create jobs, manage listings, and rank applicants.
- Candidates upload resumes, browse jobs, and apply.
- The platform computes semantic + skill-based fit scores with actionable recommendations.

## Highlights

- Role-based authentication (`recruiter`, `candidate`)
- Resume upload and parsing (PDF)
- Job creation, edit, and delete
- Candidate job application flow
- AI ranking engine with:
  - Semantic similarity scoring
  - Skill coverage scoring
  - Recommendation labels (`Strong Fit`, `Consider`, `Low Fit`)
  - Matched/missing skills output
- Clean React dashboard UI with recruiter and candidate journeys

## Tech Stack

### Frontend
- React + Vite
- React Router
- Axios

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- spaCy (`en_core_web_sm`)
- Sentence Transformers (`all-MiniLM-L6-v2`)
- scikit-learn (cosine similarity)

## Project Structure

```text
resume_ai/
├── ats-frontend/         # React frontend
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── api/
├── backend/              # FastAPI backend
│   ├── main.py
│   ├── routes.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   └── database.py
├── logs/
├── uploads/
├── requirements.txt
└── .env
```

## Setup

## 1) Clone and Enter Project

```bash
git clone <your-repo-url>
cd resume_ai
```

## 2) Backend Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Create `.env` in project root:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/resume_ai
SECRET_KEY=change_me_to_a_strong_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173
```

Start backend:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

## 3) Frontend Setup

```bash
cd ats-frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`  
Backend docs: `http://127.0.0.1:8000/docs`

## Core Workflow

1. Register/Login as recruiter or candidate.
2. Recruiter creates job descriptions.
3. Candidate uploads resume and applies to jobs.
4. Recruiter runs ranking for a job.
5. System returns ranked results with fit signals and recommendations.

## Ranking Output Explained

- `Semantic`: contextual similarity between resume and job content.
- `Skill`: explicit skill coverage match.
- `Overall`: weighted blend of semantic + skill scores.
- `Recommendation`:
  - `Strong Fit`: high confidence match
  - `Consider`: moderate fit with gaps
  - `Low Fit`: weak fit or missing required signals

## API Endpoints (Key)

Auth:
- `POST /register`
- `POST /login`
- `GET /me`

Jobs:
- `POST /create-job`
- `GET /jobs`
- `PUT /jobs/{job_id}`
- `DELETE /jobs/{job_id}`

Resumes & Applications:
- `POST /upload-resume`
- `GET /my-resumes`
- `POST /apply/{job_id}/{resume_id}`
- `GET /my-applications`

Ranking:
- `POST /rank-applicants/{job_id}?page=1&limit=10`

## Troubleshooting

- Backend not reachable:
  - Ensure FastAPI is running on `127.0.0.1:8000`.
- DB errors:
  - Check `DATABASE_URL` and PostgreSQL service status.
- CORS issues:
  - Confirm frontend URL is included in `ALLOWED_ORIGINS`.
- Model load delays:
  - First semantic scoring call may take longer while model initializes.

## Security Notes

- Replace `SECRET_KEY` in production.
- Restrict `ALLOWED_ORIGINS` to trusted domains.
- Use HTTPS in production.
- Store uploaded files in secure storage (S3/GCS) for production environments.

## Future Improvements

- Alembic migrations for schema versioning
- Recruiter analytics dashboard
- Resume section-level explainability
- Batch ranking and export features

---

Built to streamline hiring with practical AI signals and a clean recruiter-candidate workflow.

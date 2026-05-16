<h1 align="center">Intelligent ATS Platform</h1>
<p align="center">
  AI-powered Applicant Tracking System for smarter hiring decisions
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Frontend-React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/NLP-spaCy-09A3D5?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Embeddings-SentenceTransformers-FF6F61?style=for-the-badge" />
</p>

---

## Overview

**Intelligent ATS Platform** helps recruiters and candidates collaborate in one streamlined workflow:

- Recruiters create jobs, manage listings, and rank applicants
- Candidates upload resumes and apply to relevant roles
- AI scoring combines **semantic match** + **skill coverage** + **recommendation labels**

---

## Core Features

- Role-based authentication (`recruiter`, `candidate`)
- Resume upload and parsing (PDF)
- Job create/edit/delete
- Candidate application workflow
- Applicant ranking engine with:
  - Semantic score
  - Skill score
  - Overall score
  - Recommendation (`Strong Fit`, `Consider`, `Low Fit`)
  - Matched/missing skills output

---

## Quick Preview


## Quick Preview

<p align="center">
  <img src="assets/dashboard.png" width="800"/>
</p>

<p align="center">
  <img src="assets/rank.png" width="800"/>
</p>

## Tech Stack

### Frontend
- React
- Vite
- React Router
- Axios

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn

### AI/NLP
- spaCy (`en_core_web_sm`)
- Sentence Transformers (`all-MiniLM-L6-v2`)
- scikit-learn (cosine similarity)

### Language
- Python
- JavaScript

## Project Structure

```text
resume_ai/
├── ats-frontend/
├── backend/
├── requirements.txt
└── .env
Setup
1) Clone
bash

git clone https://github.com/likhith-099/Intelligent-Ats-Platform.git
cd Intelligent-Ats-Platform
2) Backend
bash

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
Create .env in root:

env

DATABASE_URL=postgresql://postgres:password@localhost:5432/resume_ai
SECRET_KEY=change_this_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
Run backend:

bash

python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
3) Frontend
bash

cd ats-frontend
npm install
npm run dev
URLs
Frontend: http://localhost:5173
Backend API Docs: http://127.0.0.1:8000/docs
Main Workflow
Register/Login as recruiter or candidate
Recruiter creates jobs
Candidate uploads resume and applies
Recruiter runs ranking
Platform returns ranked results with recommendations
Important API Endpoints
Auth
POST /register
POST /login
GET /me
Jobs
POST /create-job
GET /jobs
PUT /jobs/{job_id}
DELETE /jobs/{job_id}
Candidate
POST /upload-resume
GET /my-resumes
POST /apply/{job_id}/{resume_id}
GET /my-applications
Ranking
POST /rank-applicants/{job_id}?page=1&limit=10

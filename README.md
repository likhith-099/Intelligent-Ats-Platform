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

## 📂 Project Structure

```text
Intelligent-Ats-Platform/
│
├── ats-frontend/          # React frontend (Vite)
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/               # FastAPI backend
│   ├── main.py
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── database.py
│
├── assets/                # Screenshots for README
│   ├── dashboard.png
│   └── rank.png
│
├── requirements.txt
├── .env
└── README.md
```
---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/likhith-099/Intelligent-Ats-Platform.git
cd Intelligent-Ats-Platform
```

---

## 🔹 Backend Setup (FastAPI)

### Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Create `.env` File in Root Directory

Create a file named `.env` and add:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/resume_ai
SECRET_KEY=change_this_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Run Backend Server

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

API Docs:

```
http://127.0.0.1:8000/docs
```

---

## 🔹 Frontend Setup (React + Vite)

```bash
cd ats-frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## ✅ Main Workflow

1. Register/Login as **recruiter** or **candidate**
2. Recruiter creates jobs
3. Candidate uploads resume & applies
4. Recruiter runs ranking
5. AI returns ranked applicants with recommendations

---

## 📡 Important API Endpoints

### 🔐 Authentication

| Method | Endpoint        | Description |
|--------|----------------|-------------|
| POST   | `/register`    | Register new user (recruiter/candidate) |
| POST   | `/login`       | Login and receive access token |
| GET    | `/me`          | Get current logged-in user |

---

### 💼 Jobs (Recruiter)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/create-job` | Create new job |
| GET    | `/jobs` | Get all jobs |
| PUT    | `/jobs/{job_id}` | Update job |
| DELETE | `/jobs/{job_id}` | Delete job |

---

### 👤 Candidate

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/upload-resume` | Upload resume (PDF) |
| GET    | `/my-resumes` | Get candidate resumes |
| POST   | `/apply/{job_id}/{resume_id}` | Apply to job |
| GET    | `/my-applications` | View applied jobs |

---

### 📊 Ranking Engine

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/rank-applicants/{job_id}?page=1&limit=10` | Rank applicants using AI scoring |

---

## 🧠 Ranking Logic

The ranking engine combines:

- ✅ Semantic Similarity Score (Sentence Transformers)
- ✅ Skill Match Score
- ✅ Overall Weighted Score
- ✅ Recommendation Label:
  - `Strong Fit`
  - `Consider`
  - `Low Fit`
- ✅ Matched Skills
- ✅ Missing Skills

---

📘 Full Interactive API Documentation:

```
http://127.0.0.1:8000/docs
```

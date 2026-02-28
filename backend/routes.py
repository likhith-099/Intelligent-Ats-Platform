# ================================
# IMPORTS
# ================================

import spacy
import shutil
import os

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .database import get_db
from . import models, schemas, auth


# ================================
# ROUTER INITIALIZATION
# ================================

router = APIRouter()

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
nlp = spacy.load("en_core_web_sm")

UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# ================================
# REGISTER (WITH ROLE)
# ================================

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    if user.role not in ["recruiter", "candidate"]:
        raise HTTPException(status_code=400, detail="Role must be recruiter or candidate")

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = auth.hash_password(user.password)

    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pw,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ================================
# LOGIN
# ================================

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not db_user or not auth.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = auth.create_access_token(
        data={"sub": db_user.email}
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ================================
# CURRENT USER
# ================================

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# ================================
# UPLOAD RESUME (CANDIDATE ONLY)
# ================================

@router.post("/upload-resume")
def upload_resume(file: UploadFile = File(...),
                  current_user: models.User = Depends(auth.get_current_user),
                  db: Session = Depends(get_db)):

    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can upload resumes")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    chunks = [chunk.strip() for chunk in text.split("\n") if chunk.strip()]

    chunk_embeddings = [
        embedding_model.encode(chunk).tolist()
        for chunk in chunks
    ]

    new_resume = models.Resume(
        filename=file.filename,
        content=text,
        chunks=chunks,
        chunk_embeddings=chunk_embeddings,
        user_id=current_user.id
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return {"resume_id": new_resume.id, "message": "Resume uploaded successfully"}


# ================================
# CREATE JOB (RECRUITER ONLY)
# ================================

@router.post("/create-job")
def create_job(title: str,
               description: str,
               current_user: models.User = Depends(auth.get_current_user),
               db: Session = Depends(get_db)):

    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can create jobs")

    chunks = [chunk.strip() for chunk in description.split("\n") if chunk.strip()]

    chunk_embeddings = [
        embedding_model.encode(chunk).tolist()
        for chunk in chunks
    ]

    job = models.Job(
        title=title,
        description=description,
        chunks=chunks,
        chunk_embeddings=chunk_embeddings,
        user_id=current_user.id
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return {"job_id": job.id, "message": "Job created successfully"}


# ================================
# APPLY TO JOB (CANDIDATE ONLY)
# ================================

@router.post("/apply/{job_id}/{resume_id}")
def apply_to_job(job_id: int,
                 resume_id: int,
                 current_user: models.User = Depends(auth.get_current_user),
                 db: Session = Depends(get_db)):

    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can apply")

    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job = db.query(models.Job).filter(models.Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing_application = db.query(models.Application).filter(
        models.Application.job_id == job_id,
        models.Application.resume_id == resume_id
    ).first()

    if existing_application:
        raise HTTPException(status_code=400, detail="Already applied")

    application = models.Application(
        job_id=job_id,
        resume_id=resume_id
    )

    db.add(application)
    db.commit()

    return {"message": "Application submitted successfully"}


# ================================
# CORE SCORING ENGINE
# ================================

def compute_resume_score(resume, job):

    max_similarity = 0
    best_chunk = ""

    for r_chunk, r_embedding in zip(resume.chunks, resume.chunk_embeddings):
        for j_embedding in job.chunk_embeddings:
            similarity = cosine_similarity([r_embedding], [j_embedding])[0][0]

            if similarity > max_similarity:
                max_similarity = similarity
                best_chunk = r_chunk

    semantic_score = round(float(max_similarity) * 100, 2)

    doc_job = nlp(job.description)
    job_phrases = {chunk.text.lower().strip() for chunk in doc_job.noun_chunks}

    resume_lower = resume.content.lower()

    matched = [p for p in job_phrases if p in resume_lower]
    total = len(job_phrases)

    skill_alignment = round((len(matched) / total) * 100, 2) if total > 0 else 0

    overall_score = round((0.6 * semantic_score) + (0.4 * skill_alignment), 2)

    return semantic_score, skill_alignment, overall_score


# ================================
# RANK APPLICANTS (RECRUITER ONLY)
# ================================
@router.post("/rank-applicants/{job_id}")
def rank_applicants(
    job_id: int,
    page: int = 1,
    limit: int = 10,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
    ):

    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can rank applicants")

    job = db.query(models.Job).filter(
    models.Job.id == job_id,
    models.Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    applications = db.query(models.Application).filter(
        models.Application.job_id == job_id
    ).all()

    if not applications:
        raise HTTPException(status_code=404, detail="No applicants found")

    results = []

    for application in applications:
        resume = application.resume

        semantic, skill, overall = compute_resume_score(resume, job)

        results.append({
            "resume_id": resume.id,
            "filename": resume.filename,
            "semantic_score": semantic,
            "skill_alignment": skill,
            "overall_score": overall
        })

    results.sort(key=lambda x: x["overall_score"], reverse=True)

    for idx, item in enumerate(results, start=1):
        item["rank"] = idx

    total_applicants = len(results)

    start = (page - 1) * limit
    end = start + limit

    paginated_results = results[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_applicants": total_applicants,
        "results": paginated_results
    }
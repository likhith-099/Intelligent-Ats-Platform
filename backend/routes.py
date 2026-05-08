# ================================
# IMPORTS
# ================================

import spacy
import shutil
import os
import uuid
import re
import logging

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
import numpy as np
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from fastapi.security import OAuth2PasswordRequestForm
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.utils import secure_filename

from .database import get_db
from . import models, schemas, auth

logger = logging.getLogger(__name__)


# ================================
# ROUTER INITIALIZATION
# ================================

router = APIRouter()

embedding_model = None
nlp = None

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def get_embedding_model():
    """Load the transformer model only when a scoring/upload endpoint needs it."""
    global embedding_model
    if embedding_model is None:
        logger.info("Loading sentence transformer model")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return embedding_model


def get_nlp():
    """Load spaCy lazily so lightweight endpoints and health checks start fast."""
    global nlp
    if nlp is None:
        logger.info("Loading spaCy model")
        nlp = spacy.load("en_core_web_sm")
    return nlp


def semantic_chunk(text: str, max_chunk_size: int = 500) -> list:
    """Split text into semantic chunks preserving sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence_length = len(sentence)
        if current_length + sentence_length <= max_chunk_size:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def encode_chunks(chunks: list) -> list:
    model = get_embedding_model()
    return [model.encode(chunk).tolist() for chunk in chunks]


def extract_job_skills(job_description: str) -> list[str]:
    """Extract normalized skill terms from either comma-separated or prose descriptions."""
    text = (job_description or "").strip().lower()
    if not text:
        return []

    # Prefer explicit separators when present (common for skill-list style job descriptions).
    has_explicit_separators = any(sep in text for sep in [",", "\n", ";", "|"])
    if has_explicit_separators:
        parts = re.split(r"[,\n;|]+", text)
        normalized = []
        for part in parts:
            skill = re.sub(r"\s+", " ", part).strip(" .:-")
            if 1 < len(skill) <= 80:
                normalized.append(skill)
        # Deduplicate while preserving order.
        return list(dict.fromkeys(normalized))

    # Fallback for prose: noun chunks from spaCy.
    doc_job = get_nlp()(text)
    noun_chunks = []
    for chunk in doc_job.noun_chunks:
        skill = re.sub(r"\s+", " ", chunk.text.lower().strip(" .:-"))
        if 1 < len(skill) <= 80:
            noun_chunks.append(skill)
    return list(dict.fromkeys(noun_chunks))


def extract_relevant_resume_text(resume_text: str) -> str:
    """Prefer resume sections that best represent role-fit evidence."""
    text = (resume_text or "").strip()
    if not text:
        return ""

    section_heading_pattern = re.compile(
        r"^\s*(skills?|technical skills?|technologies|experience|work experience|"
        r"projects?|professional experience|summary|profile)\s*$",
        re.IGNORECASE,
    )

    lines = text.splitlines()
    sections = []
    current_heading = "general"
    current_lines = []

    for raw_line in lines:
        line = raw_line.strip()
        if section_heading_pattern.match(line):
            if current_lines:
                sections.append((current_heading.lower(), "\n".join(current_lines).strip()))
                current_lines = []
            current_heading = line
            continue
        current_lines.append(raw_line)

    if current_lines:
        sections.append((current_heading.lower(), "\n".join(current_lines).strip()))

    preferred_keywords = ("skill", "technolog", "experience", "project", "summary", "profile")
    preferred_sections = []
    fallback_sections = []

    for heading, body in sections:
        normalized_body = body.strip()
        if not normalized_body:
            continue
        if any(keyword in heading for keyword in preferred_keywords):
            preferred_sections.append(normalized_body)
        else:
            fallback_sections.append(normalized_body)

    # Use preferred sections when available, otherwise keep original resume text.
    if preferred_sections:
        return "\n".join(preferred_sections)
    if fallback_sections:
        return "\n".join(fallback_sections)
    return text


def get_resume_focus_data(resume_text: str) -> tuple[str, float, bool]:
    """Return focused text, confidence, and whether named sections were detected."""
    text = (resume_text or "").strip()
    if not text:
        return "", 0.0, False

    focused = extract_relevant_resume_text(text)
    if not focused:
        return text, 0.25, False

    # If focus text is shorter than source, we likely found targeted sections.
    total_len = max(len(text), 1)
    focus_ratio = len(focused) / total_len
    detected_sections = focus_ratio < 0.95
    confidence = 0.8 if detected_sections else 0.45
    return focused, confidence, detected_sections


def extract_must_have_skills(job_description: str, job_skills: list[str]) -> list[str]:
    """Detect must-have skills from requirement-like job description segments."""
    text = (job_description or "").lower()
    if not text or not job_skills:
        return []

    must_signal = re.compile(r"\b(must|required|mandatory|essential|need to have)\b")
    candidate_segments = re.split(r"[.\n;]+", text)
    required_segments = [segment for segment in candidate_segments if must_signal.search(segment)]

    if not required_segments:
        return []

    must_have = []
    for skill in job_skills:
        if any(skill in segment for segment in required_segments):
            must_have.append(skill)

    return list(dict.fromkeys(must_have))


# ================================
# REGISTER (WITH ROLE)
# ================================

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Registration attempt for email: {user.email}, role: {user.role}")

    if user.role not in ["recruiter", "candidate"]:
        logger.warning(f"Invalid role attempted: {user.role}")
        raise HTTPException(status_code=400, detail="Role must be recruiter or candidate")

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        logger.warning(f"Email already registered: {user.email}")
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

    logger.info(f"User registered successfully: {user.email}, id: {new_user.id}")
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

    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")

    # Secure filename with UUID to prevent collisions and path traversal
    safe_filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    # Extract text from PDF
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    # Use semantic chunking instead of line-based splitting
    chunks = semantic_chunk(text)
    if not chunks:
        try:
            os.remove(file_path)
        except OSError:
            logger.warning("Could not remove empty-text resume file: %s", file_path)
        raise HTTPException(status_code=400, detail="Could not extract readable text from this PDF")

    # Generate embeddings
    chunk_embeddings = encode_chunks(chunks)

    new_resume = models.Resume(
        filename=unique_filename,  # Store unique filename
        original_filename=file.filename,  # Store original filename for display
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
def create_job(job_data: schemas.JobCreate,
               current_user: models.User = Depends(auth.get_current_user),
               db: Session = Depends(get_db)):

    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can create jobs")

    # Use semantic chunking for better embeddings
    chunks = semantic_chunk(job_data.description)
    chunk_embeddings = encode_chunks(chunks)

    job = models.Job(
        title=job_data.title.strip(),
        description=job_data.description.strip(),
        chunks=chunks,
        chunk_embeddings=chunk_embeddings,
        user_id=current_user.id
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return {"job_id": job.id, "message": "Job created successfully"}


@router.get("/jobs", response_model=list[schemas.JobResponse])
def list_jobs(current_user: models.User = Depends(auth.get_current_user),
              db: Session = Depends(get_db)):
    query = db.query(models.Job).order_by(models.Job.id.desc())

    if current_user.role == "recruiter":
        query = query.filter(models.Job.user_id == current_user.id)

    return query.all()

@router.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    job_data: schemas.JobUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can update jobs")

    job = db.query(models.Job).filter(
        models.Job.id == job_id,
        models.Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    chunks = semantic_chunk(job_data.description)
    chunk_embeddings = encode_chunks(chunks)

    job.title = job_data.title.strip()
    job.description = job_data.description.strip()
    job.chunks = chunks
    job.chunk_embeddings = chunk_embeddings

    db.commit()
    db.refresh(job)

    return {"message": "Job updated successfully", "job_id": job.id}

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can delete jobs")

    job = db.query(models.Job).filter(
        models.Job.id == job_id,
        models.Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.query(models.Application).filter(models.Application.job_id == job.id).delete()
    db.delete(job)
    db.commit()

    return {"message": "Job deleted successfully", "job_id": job_id}


@router.get("/my-resumes", response_model=list[schemas.ResumeResponse])
def list_my_resumes(current_user: models.User = Depends(auth.get_current_user),
                    db: Session = Depends(get_db)):
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can view uploaded resumes")

    return db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id
    ).order_by(models.Resume.id.desc()).all()


@router.get("/my-applications", response_model=list[schemas.ApplicationResponse])
def list_my_applications(current_user: models.User = Depends(auth.get_current_user),
                         db: Session = Depends(get_db)):
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can view applications")

    applications = db.query(models.Application).options(
        joinedload(models.Application.job),
        joinedload(models.Application.resume)
    ).join(models.Resume).filter(
        models.Resume.user_id == current_user.id
    ).order_by(models.Application.created_at.desc()).all()

    return [
        schemas.ApplicationResponse(
            id=application.id,
            job_id=application.job_id,
            resume_id=application.resume_id,
            created_at=application.created_at,
            job_title=application.job.title,
            resume_filename=application.resume.original_filename,
        )
        for application in applications
    ]


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
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already applied")

    return {"message": "Application submitted successfully"}


# ================================
# CORE SCORING ENGINE
# ================================

def compute_resume_score(resume, job):
    # Vectorized similarity computation
    resume_focus_text, section_confidence, detected_sections = get_resume_focus_data(resume.content)
    resume_focus_chunks = semantic_chunk(resume_focus_text)
    if not resume_focus_chunks:
        resume_focus_chunks = semantic_chunk(resume.content)

    # Prefer focused chunks, then filter by job-skill relevance if possible.
    job_skills = extract_job_skills(job.description)
    must_have_skills = extract_must_have_skills(job.description, job_skills)
    if job_skills:
        filtered_chunks = []
        for chunk in resume_focus_chunks:
            chunk_lower = chunk.lower()
            if any(skill in chunk_lower for skill in job_skills):
                filtered_chunks.append(chunk)
        if filtered_chunks:
            resume_focus_chunks = filtered_chunks
            section_confidence = max(section_confidence, 0.7 if detected_sections else 0.6)

    r_embeddings = np.array(encode_chunks(resume_focus_chunks))
    j_embeddings = np.array(job.chunk_embeddings)

    if len(r_embeddings) == 0 or len(j_embeddings) == 0:
        return {
            "semantic_score": 0,
            "skill_alignment": 0,
            "overall_score": 0,
            "matched_skills": [],
            "matched_skill_count": 0,
            "total_job_skills": 0,
            "missing_skills": [],
            "recommendation": "Low Fit",
            "summary": "Resume content is insufficient for meaningful ranking.",
            "section_confidence": 0.0,
        }

    # Compute all-to-all similarity matrix
    similarities = cosine_similarity(r_embeddings, j_embeddings)
    
    # For each resume chunk, compute its best match to any job chunk.
    max_sim_per_chunk = np.max(similarities, axis=1)

    # Avoid over-penalizing long resumes with unrelated sections by focusing
    # on the strongest evidence chunks rather than averaging every chunk.
    top_k = max(3, int(np.ceil(len(max_sim_per_chunk) * 0.35)))
    top_scores = np.sort(max_sim_per_chunk)[-top_k:]
    semantic_score = round(float(np.mean(top_scores)) * 100, 2)

    # Skill Alignment
    resume_lower = resume.content.lower()

    matched = sorted([p for p in job_skills if p in resume_lower])
    missing = sorted([p for p in job_skills if p not in resume_lower])
    must_have_missing = sorted([p for p in must_have_skills if p not in resume_lower])
    total = len(job_skills)

    skill_alignment = round((len(matched) / total) * 100, 2) if total > 0 else 0
    # Slightly favor skill coverage for explicit skill-list job descriptions.
    overall_score = round((0.5 * semantic_score) + (0.5 * skill_alignment), 2)

    if overall_score >= 75:
        recommendation = "Strong Fit"
    elif overall_score >= 55:
        recommendation = "Consider"
    else:
        # If skills are very strong but semantic context is weak, keep the
        # candidate in consideration rather than outright low fit.
        recommendation = "Consider" if skill_alignment >= 80 and semantic_score >= 20 else "Low Fit"

    if must_have_missing:
        recommendation = "Low Fit"

    if recommendation == "Strong Fit":
        summary = "Good profile alignment across semantic match and required skills."
    elif recommendation == "Consider":
        summary = "Shows potential but has noticeable gaps against job requirements."
    else:
        summary = "Limited alignment with the job profile at this stage."

    # Avoid false-zero confidence on valid resumes due to parser quirks.
    if resume.content and resume.content.strip():
        section_confidence = max(section_confidence, 0.35)
    section_confidence = round(section_confidence, 2)

    return {
        "semantic_score": semantic_score,
        "skill_alignment": skill_alignment,
        "overall_score": overall_score,
        "matched_skills": matched[:12],
        "missing_skills": missing[:8],
        "matched_skill_count": len(matched),
        "total_job_skills": total,
        "must_have_skills": must_have_skills[:8],
        "must_have_missing_skills": must_have_missing[:8],
        "recommendation": recommendation,
        "summary": summary,
        "section_confidence": section_confidence,
    }


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

    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be at least 1")

    if limit < 1 or limit > 50:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 50")

    job = db.query(models.Job).filter(
    models.Job.id == job_id,
    models.Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Use joinedload to prevent N+1 query problem
    applications = db.query(models.Application).options(
        joinedload(models.Application.resume)
    ).filter(
        models.Application.job_id == job_id
    ).all()

    if not applications:
        return {
            "page": page,
            "limit": limit,
            "total_applicants": 0,
            "results": []
        }

    results = []

    for application in applications:
        resume = application.resume

        score_details = compute_resume_score(resume, job)

        results.append({
            "application_id": application.id,
            "applied_at": application.created_at.isoformat() if application.created_at else None,
            "resume_id": resume.id,
            "filename": resume.filename,
            "original_filename": resume.original_filename,
            "semantic_score": score_details["semantic_score"],
            "skill_alignment": score_details["skill_alignment"],
            "overall_score": score_details["overall_score"],
            "matched_skills": score_details["matched_skills"],
            "missing_skills": score_details["missing_skills"],
            "matched_skill_count": score_details["matched_skill_count"],
            "total_job_skills": score_details["total_job_skills"],
            "must_have_skills": score_details["must_have_skills"],
            "must_have_missing_skills": score_details["must_have_missing_skills"],
            "recommendation": score_details["recommendation"],
            "summary": score_details["summary"],
            "section_confidence": score_details["section_confidence"],
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

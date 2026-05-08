from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from .database import Base
from sqlalchemy import UniqueConstraint

# ================================
# USER MODEL (Recruiter / Candidate)
# ================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    resumes = relationship("Resume", back_populates="user")
    jobs = relationship("Job", back_populates="user")

# ================================
# RESUME MODEL (Owned by Candidate)
# ================================

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)  # Unique stored filename
    original_filename = Column(String, nullable=False)  # Original uploaded filename
    content = Column(Text, nullable=False)

    chunks = Column(JSON, nullable=False)
    chunk_embeddings = Column(JSON, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship("User", back_populates="resumes")

    applications = relationship("Application", back_populates="resume")
    
    __table_args__ = (
        Index('ix_resumes_user_id_created', user_id),  # Composite index if we had created_at
    )

# ================================
# JOB MODEL (Created by Recruiter)
# ================================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)

    chunks = Column(JSON, nullable=False)
    chunk_embeddings = Column(JSON, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship("User", back_populates="jobs")

    applications = relationship("Application", back_populates="job")
    
    __table_args__ = (
        Index('ix_jobs_user_id_title', user_id, title),
    )
# ================================
# APPLICATION MODEL (Resume ↔ Job Mapping)
# ================================





class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('job_id', 'resume_id', name='unique_application'),
        Index('ix_applications_job_id_created', job_id, created_at),
        Index('ix_applications_resume_id_created', resume_id, created_at),
    )

    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
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
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    chunks = Column(JSON, nullable=False)
    chunk_embeddings = Column(JSON, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="resumes")

    applications = relationship("Application", back_populates="resume")

# ================================
# JOB MODEL (Created by Recruiter)
# ================================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    chunks = Column(JSON, nullable=False)
    chunk_embeddings = Column(JSON, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="jobs")

    applications = relationship("Application", back_populates="job")
# ================================
# APPLICATION MODEL (Resume ↔ Job Mapping)
# ================================





class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint('job_id', 'resume_id', name='unique_application'),
    )

    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
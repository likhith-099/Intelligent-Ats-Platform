from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import re


# ============================
# USER SCHEMAS
# ============================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: str   # "recruiter" or "candidate"
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @field_validator('role')
    @classmethod
    def valid_role(cls, v):
        if v not in ["recruiter", "candidate"]:
            raise ValueError('Role must be recruiter or candidate')
        return v


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


# ============================
# JOB SCHEMAS
# ============================

class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)

class JobUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int

    class Config:
        from_attributes = True


class ResumeResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    user_id: int

    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    resume_id: int
    created_at: datetime
    job_title: str
    resume_filename: str


# ============================
# TOKEN SCHEMA
# ============================

class Token(BaseModel):
    access_token: str
    token_type: str

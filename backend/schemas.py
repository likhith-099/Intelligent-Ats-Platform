from pydantic import BaseModel, EmailStr
from typing import Optional


# ============================
# USER SCHEMAS
# ============================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str   # "recruiter" or "candidate"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


# ============================
# TOKEN SCHEMA
# ============================

class Token(BaseModel):
    access_token: str
    token_type: str
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
import backend.models
from .routes import router
from .rate_limiter import rate_limit_middleware
from .logging_config import setup_logging
from sqlalchemy import inspect, text
import os
import logging

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

Base.metadata.create_all(bind=engine)

def ensure_schema_compatibility():
    inspector = inspect(engine)

    if "applications" not in inspector.get_table_names():
        return

    with engine.begin() as conn:
        app_columns = {col["name"] for col in inspector.get_columns("applications")}
        if "created_at" not in app_columns:
            logger.warning("Missing applications.created_at column detected; applying compatibility migration")
            conn.execute(
                text(
                    "ALTER TABLE applications "
                    "ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()"
                )
            )

        if "resumes" in inspector.get_table_names():
            resume_columns = {col["name"] for col in inspector.get_columns("resumes")}
            if "original_filename" not in resume_columns:
                logger.warning("Missing resumes.original_filename column detected; applying compatibility migration")
                conn.execute(
                    text("ALTER TABLE resumes ADD COLUMN original_filename TEXT")
                )
                conn.execute(
                    text("UPDATE resumes SET original_filename = filename WHERE original_filename IS NULL")
                )
                conn.execute(
                    text("ALTER TABLE resumes ALTER COLUMN original_filename SET NOT NULL")
                )

ensure_schema_compatibility()

# Get allowed origins from environment variable
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not ALLOWED_ORIGINS or ALLOWED_ORIGINS == [""]:
    ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "API running"}
#####################################################################

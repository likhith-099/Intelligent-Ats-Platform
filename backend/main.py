from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
import backend.models
from .routes import router
from .rate_limiter import rate_limit_middleware
from .logging_config import setup_logging
import os
import logging

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

Base.metadata.create_all(bind=engine)

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

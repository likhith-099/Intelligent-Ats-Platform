from fastapi import FastAPI
from .database import engine, Base
import backend.models
from .routes import router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "API running"}
#####################################################################

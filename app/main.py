from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()
app = FastAPI(title="Agente Virtual UNAB")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"status": "ok", "service": "Agente Virtual UNAB"}
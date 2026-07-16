# -*- coding: utf-8 -*-
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("unab_rag_agent")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

settings = get_settings()

app = FastAPI(
    title="Agente Virtual UNAB",
    description="Asistente institucional basado en RAG para la Universidad Doctor Andrés Bello.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API del agente (chat, health, etc.)
app.include_router(api_router)

@app.on_event("startup")
def warm_up():
    """
    Precarga los modelos/clientes pesados (embeddings, retriever, LLMs) al
    iniciar el proceso, para que la primera petición de un usuario no
    pague el costo de inicialización.
    """
    from app.core.rag_chain import _get_multi_retriever, _get_response_chain
    from app.core.classifier import _get_classifier_chain

    logger.info("Precargando componentes del agente UNAB...")
    _get_classifier_chain()
    _get_multi_retriever()
    _get_response_chain()
    logger.info("Componentes listos.")

# -*- coding: utf-8 -*-
import logging

from fastapi import APIRouter, HTTPException

from app.core.rag_chain import answer_query
from app.models.schemas import ChatRequest, ChatResponse, HealthResponse

logger = logging.getLogger("unab_rag_agent")

router = APIRouter(prefix="/api", tags=["agente"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")

    try:
        result = answer_query(query)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error procesando la consulta: %s", query)
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error procesando tu consulta. Intenta nuevamente en unos minutos.",
        ) from exc

    return ChatResponse(**result)

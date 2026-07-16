# -*- coding: utf-8 -*-
"""
Orquestación del flujo RAG del agente UNAB.

Flujo:
1. Clasificación (Cohere)        -> ¿la pregunta es institucional?
   - Si NO -> se responde de inmediato con el mensaje de fuera de alcance.
     Esto evita generar las 5 sub-consultas del multiquery y consultar
     el vector store, ahorrando tokens y latencia.
2. Multiquery (Gemini)           -> genera variaciones de la pregunta y
   recupera fragmentos desde Pinecone usando el retriever base.
3. Si no se recupera contexto    -> mensaje de "contexto insuficiente".
4. Respuesta final (Gemini)      -> usando el prompt del asistente UNAB
   con el contexto recuperado.
"""

import logging
from functools import lru_cache
from typing import TypedDict

from langchain_classic.retrievers import MultiQueryRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings
from app.core.classifier import is_institutional_query
from app.core.prompts import (
    MULTIQUERY_PROMPT,
    OUT_OF_SCOPE_MESSAGE,
    RESPONSE_PROMPT,
    build_insufficient_context_message,
)
from app.core.vectorstore import get_base_retriever

logger = logging.getLogger("unab_rag_agent")

class RagAnswer(TypedDict):
    answer: str
    classification: str  # "institucional" | "fuera_de_alcance"
    used_multiquery: bool
    num_fragments: int


@lru_cache
def _get_gemini_llm() -> ChatGoogleGenerativeAI:
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        temperature=0.1,
    )


@lru_cache
def _get_multi_retriever() -> MultiQueryRetriever:
    return MultiQueryRetriever.from_llm(
        retriever=get_base_retriever(),
        llm=_get_gemini_llm(),
        prompt=MULTIQUERY_PROMPT,
    )


@lru_cache
def _get_response_chain():
    return RESPONSE_PROMPT | _get_gemini_llm() | StrOutputParser()

def answer_query(query: str) -> RagAnswer:
    settings = get_settings()

    # --- 1. Clasificación previa (Cohere) ---
    if not is_institutional_query(query):
        logger.info("Consulta clasificada como FUERA_DE_ALCANCE: %s", query)
        return RagAnswer(
            answer=OUT_OF_SCOPE_MESSAGE,
            classification="fuera_de_alcance",
            used_multiquery=False,
            num_fragments=0,
        )

    # --- 2. Multiquery + recuperación (Gemini + Pinecone) ---
    fragmentos = _get_multi_retriever().invoke(query)

    if not fragmentos:
        logger.info("Sin fragmentos relevantes para: %s", query)
        return RagAnswer(
            answer=build_insufficient_context_message(
                settings.contacto_email, settings.contacto_telefono
            ),
            classification="institucional",
            used_multiquery=True,
            num_fragments=0,
        )

    contexto = "\n\n".join(fragmento.page_content for fragmento in fragmentos)

    # --- 3. Respuesta final (Gemini) ---
    resultado = _get_response_chain().invoke(
        {
            "query": query,
            "contexto": contexto,
            "contacto_email": settings.contacto_email,
            "contacto_telefono": settings.contacto_telefono,
        }
    )

    return RagAnswer(
        answer=resultado,
        classification="institucional",
        used_multiquery=True,
        num_fragments=len(fragmentos),
    )

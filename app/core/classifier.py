# -*- coding: utf-8 -*-
"""
Clasificador de intención.

Se ejecuta ANTES del MultiQueryRetriever. Si la pregunta no es institucional,
el flujo corta inmediatamente y NO se gastan tokens generando 5 sub-consultas
ni se consulta el vectorstore.
"""

from functools import lru_cache

from langchain_cohere import ChatCohere
from langchain_core.output_parsers import StrOutputParser

from app.config import get_settings
from app.core.prompts import CLASSIFIER_PROMPT

@lru_cache
def _get_classifier_llm() -> ChatCohere:
    settings = get_settings()
    return ChatCohere(
        cohere_api_key=settings.cohere_api_key,
        model=settings.cohere_model,
        temperature=0,
    )

@lru_cache
def _get_classifier_chain():
    return CLASSIFIER_PROMPT | _get_classifier_llm() | StrOutputParser()

def is_institutional_query(query: str) -> bool:
    """
    Devuelve True si la pregunta corresponde a un tema institucional/
    universitario, False en caso contrario. Ante cualquier duda o
    respuesta ambigua del clasificador, se asume True (fail-open) para
    no bloquear consultas legítimas por un error de parsing.
    """
    chain = _get_classifier_chain()
    raw = chain.invoke({"question": query}).strip().upper()

    if "FUERA_DE_ALCANCE" in raw or "FUERA DE ALCANCE" in raw:
        return False
    return True
# -*- coding: utf-8 -*-
"""
Clasificador de intención.

Se ejecuta ANTES del MultiQueryRetriever y distingue 3 categorias:
"saludo", "institucional" y "fuera_de_alcance". Solo si la categoria es
"institucional" se continua con el multiquery y la consulta al vector
store; para "saludo" y "fuera_de_alcance" el flujo corta de inmediato,
sin gastar tokens en las 5 sub-consultas ni consultar Pinecone.
 
Este modulo tambien expone la cadena de saludo dinamico , que genera una 
respuesta breve segun el saludo especifico recibido del usuario.
"""

from functools import lru_cache
from typing import Literal

from langchain_cohere import ChatCohere
from langchain_core.output_parsers import StrOutputParser

from app.config import get_settings
from app.core.prompts import CLASSIFIER_PROMPT, GREETING_PROMPT

QueryCategory = Literal["saludo", "capacidades", "institucional", "fuera_de_alcance"]

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

@lru_cache
def _get_greeting_chain():
    return GREETING_PROMPT | _get_classifier_llm() | StrOutputParser()

def classify_query(query: str) -> QueryCategory:
    """
    Clasifica el mensaje del usuario en una de tres categorias.
 
    Ante una respuesta ambigua o inesperada del clasificador, se falla
    hacia "institucional" (fail-open): es preferible que un saludo
    ambiguo dispare el flujo completo de busqueda (peor UX pero seguro)
    a que una pregunta institucional real se trate como saludo y nunca
    se busque en los documentos oficiales.
    """
    chain = _get_classifier_chain()
    raw = chain.invoke({"question": query}).strip().upper()

    if "SALUDO" in raw:
        return "saludo"
    if "CAPACIDADES" in raw:
        return "capacidades"
    if "FUERA_DE_ALCANCE" in raw or "FUERA DE ALCANCE" in raw:
        return "fuera_de_alcance"
    return "institucional"

def generate_greeting_response(query: str) -> str:
    """
    Genera una respuesta de saludo dinamica y breve, en base
    al mensaje exacto que escribio el usuario.
    """
    chain = _get_greeting_chain()
    return chain.invoke({"question": query}).strip()
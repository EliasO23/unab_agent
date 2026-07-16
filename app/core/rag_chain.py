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

from functools import lru_cache

from langchain_classic.retrievers import MultiQueryRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_settings
from app.core.prompts import MULTIQUERY_PROMPT
from app.core.vectorstore import get_base_retriever

@lru_cache
def _get_gemini_llm():
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        api_key=settings.gemini_api_key, 
        model=settings.gemini_model, 
        temperature=0.1
        )

@lru_cache
def _get_multi_retriever():
    return MultiQueryRetriever.from_llm(
        retriever=get_base_retriever(), 
        llm=_get_gemini_llm(), 
        prompt=MULTIQUERY_PROMPT
        )
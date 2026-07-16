# -*- coding: utf-8 -*-
"""
Punto único de acceso al VectorStore (Pinecone).
El modelo de embeddings se carga una sola vez (singleton) porque su carga
es costosa (descarga/inicialización del modelo de HuggingFace).
"""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

from app.config import get_settings

@lru_cache
def get_embeddings() -> HuggingFaceEmbeddings:
    settings = get_settings()
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)

@lru_cache
def get_vector_store() -> PineconeVectorStore:
    settings = get_settings()
    return PineconeVectorStore(
        embedding=get_embeddings(),
        host=settings.pinecone_host,
        pinecone_api_key=settings.pinecone_api_key,
    )
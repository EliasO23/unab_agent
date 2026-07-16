# -*- coding: utf-8 -*-
"""
Configuración centralizada de la aplicación.
Todas las credenciales y parámetros sensibles se cargan desde variables
de entorno (.env en local, OCI Vault / variables de entorno del
contenedor en producción). Nunca se hardcodean API keys.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
     # --- Pinecone ---
    pinecone_api_key: str
    pinecone_host: str
    pinecone_index: str = "unab-rag-agent"

    # --- Embeddings ---
    embedding_model: str = "intfloat/multilingual-e5-small"

    # --- Retrieval ---
    retriever_k: int = 4

    # --- App ---
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

@lru_cache
def get_settings() -> Settings:
    """Singleton de configuración (se carga una sola vez)."""
    return Settings()

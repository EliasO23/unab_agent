# -*- coding: utf-8 -*-
"""
Configuración centralizada de la aplicación.
Todas las credenciales y parámetros sensibles se cargan desde variables
de entorno (.env en local, OCI Vault / variables de entorno del
contenedor en producción). Nunca se hardcodean API keys.
"""

from functools import lru_cache


class Settings():

    # --- App ---
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: str = "*"

@lru_cache
def get_settings() -> Settings:
    """Singleton de configuración (se carga una sola vez)."""
    return Settings()

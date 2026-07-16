# -*- coding: utf-8 -*-
"""
Prueba manual: recupera un vector especifico de Pinecone por su ID exacto
usando el SDK de Pinecone directamente (index.fetch), sin pasar por
similarity_search (que busca por similitud, no por ID).

Util para verificar que la ingesta subio correctamente un fragmento
puntual y para inspeccionar su metadata (texto original, fuente, pagina).

Uso:
    python -m tests.test_fetch_vector
    python -m tests.test_fetch_vector <otro-id>
"""

import sys
from pinecone import Pinecone

from app.config import get_settings
from app.core.vectorstore import get_vector_store

# ID de ejemplo dado por el usuario, usado si no se pasa uno por argumento
DEFAULT_VECTOR_ID = "2223efb8-6f5b-499e-9d1b-e91394899fec"


def fetch_vector_by_id(vector_id: str):
    """Recupera un vector puntual desde Pinecone dado su ID exacto."""
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index)

    result = index.fetch(ids=[vector_id])
    vectors = result.vectors  # dict: {id: Vector(id, values, metadata)}

    if vector_id not in vectors:
        print(f"❌ No se encontró ningún vector con el ID: {vector_id}")
        print("   Verifica que el ID exista en el índice y que PINECONE_INDEX "
              "en tu .env apunte al índice correcto.")
        return None

    vector = vectors[vector_id]
    metadata = vector.metadata or {}

    print(f"✅ Vector encontrado: {vector_id}")
    print(f"   Dimensión del embedding: {len(vector.values)}")
    print("   Metadata:")
    for key, value in metadata.items():
        # El contenido del fragmento suele venir en la clave 'text'
        # (es la clave por defecto que usa langchain-pinecone).
        if key == "text":
            continue
        print(f"     - {key}: {value}")

    texto = metadata.get("text", "")
    if texto:
        print("\n   Contenido del fragmento:")
        print(f"   {texto}")
    else:
        print("\n   (El vector no tiene texto asociado en la metadata)")
    
    stats = index.describe_index_stats()
    print("\n   Stats del índice:")
    print(f"     - Total de vectores: {stats['total_vector_count']}")

    return vector


if __name__ == "__main__":
    vector_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_VECTOR_ID
    fetch_vector_by_id(vector_id)
# -*- coding: utf-8 -*-
"""
Script de ingestión de documentos institucionales.

Equivale a las celdas de "Extracción de contenido", "Fragmentación" y
"VectorStore" y se ejecuta como proceso independiente (offline), 
NO en cada arranque del servidor web.

Uso:
    python -m app.ingestion.ingest                # agrega nuevos documentos
    python -m app.ingestion.ingest --reset         # borra el índice y recarga todo

Coloca los PDF / TXT / MD oficiales en la carpeta ./documentos antes de
ejecutar este script.
"""

import argparse
import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from pinecone import Pinecone

from app.config import get_settings
from app.core.vectorstore import get_embeddings, get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("unab_ingestion")

DOCUMENTOS_DIR = Path(__file__).resolve().parent.parent.parent / "documentos"

def cargar_documentos(carpeta: Path):
    docs = []
    for archivo in carpeta.iterdir():
        ext = archivo.suffix.lower()
        loader = None
        try:
            if ext == ".pdf":
                loader = PyPDFLoader(str(archivo))
            elif ext in (".txt", ".md"):
                loader = TextLoader(str(archivo), encoding="utf-8")
            else:
                logger.info(f"Archivo {archivo.name} no cargado (formato no soportado: {ext})")
                continue
        except Exception:
            logger.exception(f"Error al cargar {archivo.name}")
            continue

        logger.info(f"Cargando {archivo.name} con {len(loader.load())} páginas")
        docs.extend(loader.load())

    logger.info(f"Total de páginas cargadas: {len(docs)}")
    return docs

def fragmentar(docs):
    embeddings = get_embeddings()
    splitter = SemanticChunker(embeddings)
    chunks = splitter.split_documents(docs)
    logger.info(f"Total de fragmentos: {len(chunks)}")
    return chunks

def resetear_indice():
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index)
    logger.info("Eliminando todos los vectores existentes del índice...")
    index.delete(delete_all=True)
    logger.info(f"Índice limpio. Stats: {index.describe_index_stats()}")


def main():
    parser = argparse.ArgumentParser(description="Ingesta de documentos institucionales a Pinecone.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Borra todos los vectores existentes antes de volver a indexar.",
    )
    parser.add_argument(
        "--carpeta",
        type=str,
        default=str(DOCUMENTOS_DIR),
        help="Ruta a la carpeta con los documentos oficiales (PDF/TXT/MD).",
    )
    args = parser.parse_args()

    carpeta = Path(args.carpeta)
    if not carpeta.exists():
        raise SystemExit(f"La carpeta de documentos no existe: {carpeta}")

    if args.reset:
        resetear_indice()

    docs = cargar_documentos(carpeta)
    if not docs:
        logger.warning("No se encontraron documentos válidos en %s", carpeta)
        return

    chunks = fragmentar(docs)

    vector_store = get_vector_store()
    logger.info("Subiendo %d fragmentos a Pinecone...", len(chunks))
    vector_store.add_documents(chunks)
    
    stats = vector_store.index.describe_index_stats()
    logger.info("Ingesta completada correctamente.")
    logger.info(f"Total de vectores en el índice: {stats['total_vector_count']}")


if __name__ == "__main__":
    main()

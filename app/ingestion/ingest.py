from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

from app.config import get_settings

def cargar_documentos(carpeta: Path):
    docs = []
    for archivo in carpeta.iterdir():
        ext = archivo.suffix.lower()
        try:
            if ext == ".pdf":
                loader = PyPDFLoader(str(archivo))
                print(f"Cargando {archivo.name} con {len(loader.load())} páginas")
            elif ext in (".txt", ".md"):
                loader = TextLoader(str(archivo), encoding="utf-8")
                print(f"Cargando {archivo.name} con {len(loader.load())} páginas")
            else:
                print(f"Archivo {archivo.name} no cargado")
                continue
        except Exception as e:
            print(f"Error al cargar {archivo.name}: {e}")
            continue
        docs.extend(loader.load())
    print(f"Total de páginas cargadas: {len(docs)}")
    print(docs[4].page_content[:100])
    return docs

def fragmentar(docs):
    embeddings = HuggingFaceEmbeddings(model_name=get_settings().embedding_model)
    chunks = SemanticChunker(embeddings).split_documents(docs)
    print(f"Total de fragmentos: {len(chunks)}")
    return chunks

if __name__ == "__main__":
    documentos = cargar_documentos(Path("documentos"))
    fragmentos = fragmentar(documentos)
    print(fragmentos[8])
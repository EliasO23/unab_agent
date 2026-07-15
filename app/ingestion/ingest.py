from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader

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
    return docs

if __name__ == "__main__":
    cargar_documentos(Path("documentos"))
FROM python:3.11-slim

# Evita bytecode y buffers, reduce tamaño de imagen
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# Dependencias del sistema necesarias para pypdf / sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# sentence-transformers arrastra torch, que por defecto en Linux instala
# paquetes CUDA (varios GB) aunque el servidor no tenga GPU. Se instala
# primero la rueda CPU-only de PyTorch para evitar ese peso innecesario.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static

# La carpeta de documentos se monta como volumen en producción para
# poder actualizar reglamentos sin reconstruir la imagen (ver docker-compose).
COPY documentos ./documentos

EXPOSE 8000

# Un solo worker: los LLM/embeddings son singletons en memoria (lru_cache).
# Para más concurrencia, escalar horizontalmente con varias instancias del
# contenedor detrás del Load Balancer de OCI en vez de aumentar workers.
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"

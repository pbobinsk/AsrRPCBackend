# CUDA 11.8 z cuDNN 8 na Ubuntu 22.04 (zgodne z torch+cu118)
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Ustaw zmienne środowiskowe
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Zaktualizuj system i zainstaluj podstawowe zależności
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python i narzędzia (Python 3.10)
    python3.10 \
    python3-pip \
    python3.10-dev \
    python3.10-venv \
    # Kompilatory i narzędzia budowania
    build-essential \
    cmake \
    git \
    wget \
    curl \
    # Biblioteki audio (dla whisper, torchaudio, pyannote)
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    sox \
    libsox-dev \
    libsox-fmt-all \
    portaudio19-dev \
    libasound2-dev \
    # Dodatkowe dla NeMo
    libopenmpi-dev \
    openmpi-bin \
    openmpi-common \
    libhdf5-dev \    
    # Biblioteki video/image (dla torchvision)
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libjpeg-dev \
    libpng-dev \
    # Biblioteki numeryczne i scientyficzne
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    # Inne przydatne
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    # Czyszczenie
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Skopiuj requirements.txt
COPY requirements.txt /tmp/requirements.txt

# Zainstaluj zależności Pythona
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Utwórz katalog roboczy
WORKDIR /app

# Skopiuj kod aplikacji
COPY . /app

# Port dla JSON-RPC (jeśli używasz)
EXPOSE 5669

# Komenda startowa (dostosuj do swojej aplikacji)
CMD ["python3", "-m", "rpc_service.rpc_server"]
# ============================================================
# Dockerfile pour Hugging Face Spaces (DeepFace API)
# ============================================================

FROM python:3.10-slim

# Variables utiles
ENV PYTHONUNBUFFERED=1
ENV TF_CPP_MIN_LOG_LEVEL=3

# Répertoire de travail
WORKDIR /app

# Dépendances système (OpenCV + DeepFace)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copier tous les fichiers
COPY . .

# Installer dépendances Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Port Hugging Face
ENV PORT=7860

# Lancer l'application Flask
CMD ["python", "app.py"]

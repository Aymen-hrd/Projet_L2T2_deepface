# ============================================================
# Dockerfile pour Hugging Face Spaces
# Déploie deepface_server.py sur un Space Docker
# ============================================================

FROM python:3.10-slim

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système nécessaires pour OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers
COPY requirements.txt .
COPY deepface_server.py .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Port exposé (7860 = port par défaut Hugging Face Spaces)
EXPOSE 7860

# Lancement du serveur
CMD ["python", "deepface_server.py"]

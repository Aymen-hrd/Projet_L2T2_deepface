# ============================================================
# DOCKERFILE POUR HUGGING FACE SPACES - SERVEUR DEEPFACE
# ============================================================

# Image Python légère basée sur Debian.
# Python 3.10 est utilisé car DeepFace, TensorFlow et leurs dépendances
# sont généralement compatibles avec cette version.
FROM python:3.10-slim


# ============================================================
# VARIABLES D'ENVIRONNEMENT
# ============================================================

# Force Python à afficher directement les logs sans les mettre en mémoire tampon.
# Utile sur Hugging Face pour voir les logs en temps réel.
ENV PYTHONUNBUFFERED=1

# Réduit les logs TensorFlow.
# Niveau 3 = masque la majorité des messages d'information et warnings.
ENV TF_CPP_MIN_LOG_LEVEL=3


# ============================================================
# RÉPERTOIRE DE TRAVAIL
# ============================================================

# Définit /app comme dossier principal dans le conteneur.
# Toutes les commandes suivantes seront exécutées depuis ce dossier.
WORKDIR /app


# ============================================================
# DÉPENDANCES SYSTÈME
# ============================================================

# Installe les bibliothèques système nécessaires à OpenCV, DeepFace et TensorFlow.
# Elles permettent notamment de décoder les images et d'exécuter les traitements
# dans une image Docker Linux minimale.
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*


# ============================================================
# COPIE DES FICHIERS DU PROJET
# ============================================================

# Copie tous les fichiers du projet dans le dossier /app du conteneur.
# Cela inclut app.py, requirements.txt et les éventuels fichiers de configuration.
COPY . .


# ============================================================
# INSTALLATION DES DÉPENDANCES PYTHON
# ============================================================

# Met pip à jour avant d'installer les bibliothèques Python.
RUN pip install --no-cache-dir --upgrade pip

# Installe toutes les dépendances listées dans requirements.txt.
# --no-cache-dir évite de garder le cache pip et réduit la taille de l'image.
RUN pip install --no-cache-dir -r requirements.txt


# ============================================================
# PORT HUGGING FACE
# ============================================================

# Hugging Face Spaces expose généralement les applications web sur le port 7860.
ENV PORT=7860


# ============================================================
# LANCEMENT DU SERVEUR
# ============================================================

# Lance le serveur Flask DeepFace.
# Le fichier app.py doit contenir app.run(host="0.0.0.0", port=PORT).
CMD ["python", "app.py"]

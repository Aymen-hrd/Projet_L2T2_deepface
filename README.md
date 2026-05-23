# EmoTrack — Serveur DeepFace

> Service d'analyse faciale des émotions — déployé sur Hugging Face Spaces.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![HuggingFace](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=flat&logo=huggingface&logoColor=black)

Ce dépôt fait partie du projet **EmoTrack**. Le dépôt principal (application Flask) est disponible ici : [EmoTrack - Application principale](https://github.com/Aymen-hrd/Projet-L2T2-FLASK)

---

## 1. Rôle de ce dépôt

EmoTrack utilise DeepFace pour analyser les expressions faciales des étudiants en temps réel. DeepFace s'appuie sur TensorFlow — trop lourd pour tourner directement sur Render, où est hébergée l'application principale.

Ce serveur est donc déployé séparément sur Hugging Face Spaces, dans un conteneur Docker dédié. L'application principale lui envoie une image via une requête HTTP, et il retourne l'émotion détectée en JSON.

```
Application Flask (Render)
        │
        │  image base64 + clé secrète
        ▼
Serveur DeepFace (Hugging Face Spaces)
        │
        │  émotion dominante + scores JSON
        ▼
Application Flask (Render)
```

---

## 2. Fonctionnement

Le serveur expose deux routes :

| Route | Méthode | Description |
|---|---|---|
| `/health` | GET | Vérifie que le serveur est actif |
| `/analyze` | POST | Reçoit une image et retourne l'émotion détectée |

> La route `/health` est utile avant une démo pour réveiller le Space s'il s'est mis en veille.

---

## 3. Référence API

### POST /analyze

**Corps de la requête (JSON) :**
```json
{
  "image":      "data:image/jpeg;base64,/9j/4AAQ...",
  "secret_key": "votre_clé_secrète"
}
```

**Réponse en cas de succès (200) :**
```json
{
  "status":     "success",
  "emotion":    "happy",
  "confidence": 94.32,
  "all_emotions": {
    "angry": 0.12,
    "disgust": 0.03,
    "fear": 0.08,
    "happy": 94.32,
    "sad": 0.21,
    "surprise": 1.10,
    "neutral": 4.14
  }
}
```

**Réponses d'erreur possibles :**

| Code | Raison |
|---|---|
| 400 | Image manquante ou illisible |
| 403 | Clé secrète incorrecte |
| 500 | Erreur interne DeepFace |

> ⚠️ La clé secrète (`DEEPFACE_SECRET_KEY`) est partagée entre ce serveur et l'application principale. Elle protège l'endpoint contre les appels non autorisés.

---

## 4. Stack technique

- **Python 3.10**
- **Flask** — serveur web léger
- **DeepFace** — analyse faciale et détection d'émotions
- **TensorFlow CPU** — backend de DeepFace (sans GPU)
- **OpenCV** — décodage et traitement des images
- **Docker** — conteneurisation pour Hugging Face Spaces

---

## 5. Déploiement sur Hugging Face Spaces

### Prérequis
- Un compte Hugging Face
- Un Space de type **Docker**

### Étapes

**1. Créer un nouveau Space sur Hugging Face (type : Docker)**

**2. Pousser les fichiers de ce dépôt dans le Space :**
```bash
git clone https://github.com/[votre-repo]/emotrack-deepface.git
cd emotrack-deepface
git remote set-url origin https://huggingface.co/spaces/[username]/[space-name]
git push
```

**3. Définir la variable d'environnement dans les Settings du Space :**
```
DEEPFACE_SECRET_KEY=votre_clé_secrète
```

> La même clé doit être renseignée côté application Flask sur Render.

---

## 6. Lancement en local

```bash
pip install -r requirements.txt
python app.py
```

Le serveur démarre sur http://localhost:7860

---

## 7. Auteurs

Projet réalisé dans le cadre du L2 Informatique et Applications — Université Paris Cité (2025-2026)  
Encadrant : M. Gnaho

- Lisa Swiatek-Hugon
- Gabrielle David
- William Ourfahli
- Aymen Herda

# Module standard Python permettant d'accéder aux variables d'environnement
import os

# Réduit les logs TensorFlow.
# Niveau 3 = masque la majorité des messages d'information et warnings.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Force TensorFlow / DeepFace à utiliser le CPU au lieu du GPU.
# Utile sur Hugging Face Spaces si le Space ne dispose pas de GPU.
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


# Module standard pour décoder l'image reçue en base64
import base64

# NumPy permet de transformer les bytes de l'image en tableau exploitable par OpenCV
import numpy as np

# OpenCV permet de décoder l'image et de la convertir en format analysable
import cv2

# Flask sert à créer le serveur web qui reçoit les requêtes depuis l'application principale
from flask import Flask, request, jsonify

# DeepFace est utilisé pour analyser l'émotion dominante sur une image
from deepface import DeepFace


# ============================================================
# SERVEUR DEEPFACE - Déployé sur Hugging Face Spaces
#
# Ce serveur reçoit une image base64 depuis app.py, hébergé sur Render.
# Il analyse l'émotion avec DeepFace, puis renvoie le résultat en JSON.
#
# Variable d'environnement à définir sur Hugging Face :
#   DEEPFACE_SECRET_KEY : clé secrète partagée avec app.py
#
# Cette clé permet d'éviter que n'importe qui appelle librement
# le serveur d'analyse faciale.
# ============================================================


# Création de l'application Flask dédiée au serveur DeepFace
app = Flask(__name__)


# Récupère la clé secrète depuis les variables d'environnement.
# La valeur par défaut sert uniquement en développement.
DEEPFACE_SECRET_KEY = os.environ.get("DEEPFACE_SECRET_KEY", "deepface-secret-key")


@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    """
    Route de vérification que le serveur est bien démarré.

    Cette route peut être appelée avant une démonstration pour réveiller
    le Space Hugging Face si celui-ci s'est mis en veille.

    Returns:
        JSON indiquant que le serveur est actif.
    """

    # Réponse simple permettant de confirmer que le serveur fonctionne
    return jsonify({
        "status": "ok",
        "message": "DeepFace server is running on Hugging Face Spaces"
    })


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Reçoit une image base64 et analyse l'émotion avec DeepFace.

    Body JSON attendu :
        - image (str)      : image encodée en base64
        - secret_key (str) : clé secrète partagée avec app.py

    Returns:
        JSON avec :
        - l'émotion dominante ;
        - le score de confiance ;
        - toutes les émotions détectées.
    """

    # Récupère le corps JSON envoyé par l'application principale
    payload = request.get_json()

    # Refuse la requête si aucun JSON n'a été envoyé
    if not payload:
        return jsonify({"error": "Missing JSON payload"}), 400

    # Vérifie que la clé secrète reçue correspond à celle configurée sur le serveur
    if payload.get("secret_key") != DEEPFACE_SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    # Récupère l'image encodée en base64 dans le JSON
    image_data = payload.get("image")

    # Refuse la requête si l'image est absente
    if not image_data:
        return jsonify({"error": "Missing image"}), 400

    try:
        # Les images envoyées par un canvas HTML peuvent contenir un préfixe :
        # "data:image/jpeg;base64,..."
        # On retire ce préfixe pour ne garder que la partie encodée.
        if "," in image_data:
            header, encoded = image_data.split(",", 1)
        else:
            encoded = image_data

        # Décode la chaîne base64 en bytes
        img_bytes = base64.b64decode(encoded)

        # Transforme les bytes en tableau NumPy
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)

        # Décode l'image avec OpenCV.
        # Le résultat est une image exploitable par DeepFace.
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Si OpenCV ne parvient pas à reconstruire l'image, on renvoie une erreur
        if img is None:
            return jsonify({
                "status": "error",
                "message": "L'image n'a pas pu être décodée"
            }), 400

        # Analyse l'émotion avec DeepFace.
        # detector_backend="opencv" est choisi car il est plus léger en ressources.
        # enforce_detection=False évite de faire planter l'analyse si aucun visage n'est détecté.
        results = DeepFace.analyze(
            img,
            actions=["emotion"],
            enforce_detection=False,
            detector_backend="opencv"
        )

        # Récupère l'émotion dominante détectée par DeepFace
        dominant_emotion = results[0]["dominant_emotion"]

        # Récupère le dictionnaire complet des scores par émotion
        emotions_dict = results[0]["emotion"]

        # Convertit toutes les valeurs NumPy en float Python standard.
        # Cela permet de les sérialiser correctement en JSON.
        emotions_dict_clean = {
            k: float(v)
            for k, v in emotions_dict.items()
        }

        # Récupère le score associé à l'émotion dominante
        confidence = float(emotions_dict[dominant_emotion])

        # Renvoie le résultat à l'application principale
        return jsonify({
            "status": "success",
            "emotion": dominant_emotion,
            "confidence": round(confidence, 2),
            "all_emotions": emotions_dict_clean
        })

    except Exception as e:
        # Affiche l'erreur côté serveur pour faciliter le débogage sur Hugging Face
        print(f"DeepFace error: {e}")

        # Retourne une erreur JSON exploitable par app.py
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# Lancement local ou lancement direct sur Hugging Face Spaces
if __name__ == "__main__":

    # Hugging Face Spaces utilise généralement le port 7860.
    # Si une variable PORT existe, elle est utilisée à la place.
    port = int(os.environ.get("PORT", 7860))

    # host="0.0.0.0" permet au serveur d'être accessible depuis l'extérieur
    app.run(host="0.0.0.0", port=port)

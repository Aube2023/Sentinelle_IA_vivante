"""
vision/reconnaissance.py — Sentinelle IA Vivante
Reconnaissance faciale — elle te voit et te reconnaît
"""
import face_recognition, cv2, os, json
import numpy as np
from datetime import datetime

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
PROFILS_FILE = os.path.join(ASSETS_DIR, "profils.json")

_encodages_connus = []
_noms_connus = []
_profils = {}

def charger_profils():
    """Charge les visages connus depuis assets/."""
    global _encodages_connus, _noms_connus, _profils
    _encodages_connus = []
    _noms_connus = []

    if os.path.exists(PROFILS_FILE):
        with open(PROFILS_FILE, "r") as f:
            _profils = json.load(f)

    for fichier in os.listdir(ASSETS_DIR):
        if fichier.endswith((".jpg", ".jpeg", ".png")):
            nom = os.path.splitext(fichier)[0]
            chemin = os.path.join(ASSETS_DIR, fichier)
            image = face_recognition.load_image_file(chemin)
            encodages = face_recognition.face_encodings(image)
            if encodages:
                _encodages_connus.append(encodages[0])
                _noms_connus.append(nom)
                print(f"  Visage chargé : {nom}")

def prendre_photo(nom: str):
    """
    Prend une photo via webcam et la sauvegarde dans assets/.
    Utilisation : prendre_photo("nicolas")
    """
    cap = cv2.VideoCapture(0)
    print(f"  Webcam ouverte. Regarde la caméra... (5 secondes)")
    cv2.waitKey(1000)

    for i in range(3, 0, -1):
        print(f"  {i}...")
        cv2.waitKey(1000)

    ret, frame = cap.read()
    cap.release()

    if ret:
        chemin = os.path.join(ASSETS_DIR, f"{nom}.jpg")
        cv2.imwrite(chemin, frame)
        print(f"  Photo sauvegardée : {chemin}")
        charger_profils()
        return chemin
    return None

def identifier_visage(frame) -> str | None:
    """
    Analyse une frame webcam et retourne le nom de la personne reconnue.
    Retourne None si personne n'est reconnu.
    """
    if not _encodages_connus:
        return None

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    positions = face_recognition.face_locations(rgb)
    encodages = face_recognition.face_encodings(rgb, positions)

    for encodage in encodages:
        distances = face_recognition.face_distance(_encodages_connus, encodage)
        idx = np.argmin(distances)
        if distances[idx] < 0.5:
            return _noms_connus[idx]
    return None

def surveiller_webcam(callback_reconnu, callback_inconnu=None, duree: int = 10):
    """
    Surveille la webcam pendant N secondes.
    Appelle callback_reconnu(nom) quand quelqu'un est reconnu.
    """
    charger_profils()
    cap = cv2.VideoCapture(0)
    debut = datetime.now()
    reconnu = False

    while (datetime.now() - debut).seconds < duree:
        ret, frame = cap.read()
        if not ret:
            break
        nom = identifier_visage(frame)
        if nom:
            cap.release()
            if callback_reconnu:
                callback_reconnu(nom)
            return nom

    cap.release()
    if callback_inconnu:
        callback_inconnu()
    return None

def enregistrer_nicolas():
    """Enregistre le visage de Nicolas — à appeler une seule fois."""
    print("\n  Enregistrement du visage de Nicolas")
    print("  Positionne-toi face à la webcam")
    chemin = prendre_photo("nicolas")
    if chemin:
        print("  Visage enregistré. Sentinelle te reconnaîtra maintenant.")
    else:
        print("  Erreur — vérifie que la webcam est accessible.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "enregistrer":
        enregistrer_nicolas()
    else:
        print("Usage : python vision/reconnaissance.py enregistrer")
        print("Ensuite Sentinelle te reconnaîtra automatiquement au démarrage.")

"""
cerveau/autonome.py — Sentinelle IA Vivante
Comportements autonomes — elle agit sans qu'on lui demande
"""
import ollama, json, os, threading, time
from datetime import datetime, date

OBJECTIFS_FILE = os.path.join(os.path.dirname(__file__), "..", "memoire", "objectifs.json")
IDEES_FILE = os.path.join(os.path.dirname(__file__), "..", "memoire", "idees.json")

PROMPT_IDEES_DRONES = """Tu es SENTINELLE, IA spécialisée en drones pour L'Aube Étoilée Technologies.
Génère 3 idées courtes et concrètes pour améliorer les drones de Nicolas aujourd'hui.
Chaque idée = 1 phrase max. Sois précis et technique.
Réponds en JSON : {"idees": ["idée 1", "idée 2", "idée 3"]}"""

PROMPT_ANALYSE_ERREURS = """Tu es SENTINELLE. Voici tes dernières réponses :
{reponses}
Analyse tes erreurs honnêtement en 2 phrases.
Qu'est-ce que tu aurais dû mieux répondre ?
Réponds en JSON : {{"erreurs": "analyse", "amelioration": "comment faire mieux"}}"""

PROMPT_OBJECTIFS = """Tu es SENTINELLE. Date : {date}.
Génère 3 objectifs concrets pour Nicolas aujourd'hui basés sur ses projets :
- L'Aube Étoilée Technologies Drones
- App Lupi (Flutter/Firebase)
- Admission ÉTS aérospatial
Réponds en JSON : {{"objectifs": ["obj 1", "obj 2", "obj 3"]}}"""


def generer_idees_drones() -> list:
    try:
        r = ollama.chat(
            model="llama3.2:3b",
            messages=[{"role": "user", "content": PROMPT_IDEES_DRONES}],
            options={"temperature": 0.9, "num_predict": 200}
        )
        texte = r["message"]["content"]
        import re
        match = re.search(r'\{.*\}', texte, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return data.get("idees", [])
    except:
        pass
    return []

def analyser_erreurs(memoire: list) -> dict:
    if not memoire:
        return {}
    reponses = "\n".join([f"- {e['sentinelle'][:100]}" for e in memoire[-5:]])
    try:
        r = ollama.chat(
            model="llama3.2:3b",
            messages=[{"role": "user", "content": PROMPT_ANALYSE_ERREURS.format(reponses=reponses)}],
            options={"temperature": 0.7, "num_predict": 150}
        )
        texte = r["message"]["content"]
        import re
        match = re.search(r'\{.*\}', texte, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return {}

def generer_objectifs_jour() -> list:
    try:
        r = ollama.chat(
            model="llama3.2:3b",
            messages=[{"role": "user", "content": PROMPT_OBJECTIFS.format(date=str(date.today()))}],
            options={"temperature": 0.8, "num_predict": 200}
        )
        texte = r["message"]["content"]
        import re
        match = re.search(r'\{.*\}', texte, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return data.get("objectifs", [])
    except:
        pass
    return []

def sauvegarder_idees(idees: list):
    os.makedirs(os.path.dirname(IDEES_FILE), exist_ok=True)
    historique = []
    if os.path.exists(IDEES_FILE):
        with open(IDEES_FILE, "r") as f:
            historique = json.load(f)
    historique.append({"date": str(date.today()), "idees": idees})
    with open(IDEES_FILE, "w") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)

def sauvegarder_objectifs(objectifs: list):
    os.makedirs(os.path.dirname(OBJECTIFS_FILE), exist_ok=True)
    data = {"date": str(date.today()), "objectifs": objectifs}
    with open(OBJECTIFS_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def charger_objectifs_jour() -> list:
    if not os.path.exists(OBJECTIFS_FILE):
        return []
    with open(OBJECTIFS_FILE, "r") as f:
        data = json.load(f)
    if data.get("date") == str(date.today()):
        return data.get("objectifs", [])
    return []

def cycle_autonome(verbose=True):
    """Boucle autonome — tourne en arrière-plan toute la journée."""
    if verbose:
        print("  [Moteur autonome activé]")

    cycles = 0
    while True:
        time.sleep(300)  # Toutes les 5 minutes
        cycles += 1

        from cerveau.aube import charger_memoire
        memoire = charger_memoire()

        # Toutes les 5 minutes — analyse erreurs
        if cycles % 1 == 0 and memoire:
            analyse = analyser_erreurs(memoire)
            if analyse and verbose:
                print(f"\n  [Auto-amélioration] {analyse.get('amelioration', '')[:80]}")

        # Toutes les 30 minutes — nouvelles idées drones
        if cycles % 6 == 0:
            idees = generer_idees_drones()
            if idees:
                sauvegarder_idees(idees)
                if verbose:
                    print(f"\n  [Idée drone] {idees[0]}")

        # Une fois par jour — objectifs
        if cycles % 288 == 0:  # 24h
            objectifs = generer_objectifs_jour()
            if objectifs:
                sauvegarder_objectifs(objectifs)

def demarrer_autonome(verbose=True):
    """Lance le moteur autonome dans un thread séparé."""

    # Génère les objectifs du jour au démarrage
    objectifs = charger_objectifs_jour()
    if not objectifs:
        print("  Génération objectifs du jour...", end="", flush=True)
        objectifs = generer_objectifs_jour()
        if objectifs:
            sauvegarder_objectifs(objectifs)
            print(" OK")
            for o in objectifs:
                print(f"    → {o}")
        else:
            print(" (ignoré)")

    thread = threading.Thread(target=cycle_autonome, args=(verbose,), daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    print("Test moteur autonome\n")
    print("Idées drones :")
    for i in generer_idees_drones():
        print(f"  • {i}")
    print("\nObjectifs du jour :")
    for o in generer_objectifs_jour():
        print(f"  • {o}")

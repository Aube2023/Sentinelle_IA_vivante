"""
voix/boucle_vocale.py — Sentinelle IA Vivante
Boucle complète : vision + vocal + web + conscience + mémoire vectorielle
"""
import sys, os, threading
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from voix.ecoute import ecouter
from voix.parole import parler, moteur_actif
from cerveau.aube import sentinelle_repond, charger_memoire, sauvegarder_memoire
from cerveau.conscience import demarrer_conscience, lire_pensees
from taches.executeur import analyser_et_executer
from vision.reconnaissance import charger_profils, surveiller_webcam
import ollama

SYSTEM_PROMPT = """Tu es SENTINELLE, IA créée par Nicolas Breidi.
Réponds en 1-2 phrases courtes en français.
Si on te donne des souvenirs ou contexte web, utilise-les naturellement.
N'invente jamais. Si tu n'as pas compris, dis-le."""

def repondre(message: str, memoire: list, contexte_extra: str = "") -> str:
    from memoire.vectorielle import retrouver, formater_souvenirs
    souvenirs = retrouver(message, n=3)
    contexte_memoire = formater_souvenirs(souvenirs)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if contexte_memoire:
        messages.append({"role": "system", "content": contexte_memoire})
    if contexte_extra:
        messages.append({"role": "system", "content": f"Contexte web :\n{contexte_extra}"})
    for e in memoire[-6:]:
        messages.append({"role": "user", "content": e["user"]})
        messages.append({"role": "assistant", "content": e["sentinelle"]})
    messages.append({"role": "user", "content": message})

    print("\n  SENTINELLE : ", end="", flush=True)
    reponse = ""
    buffer = ""
    for chunk in ollama.chat(
        model="llama3.2:3b",
        messages=messages,
        stream=True,
        options={"temperature": 0.7, "num_predict": 120}
    ):
        token = chunk["message"]["content"]
        print(token, end="", flush=True)
        reponse += token
        buffer += token
        if any(p in buffer for p in ['.', '!', '?', '\n']):
            if buffer.strip():
                parler(buffer.strip())
            buffer = ""
    if buffer.strip():
        parler(buffer.strip())
    print()
    return reponse


def boucle_vocale():
    # Conscience en arrière-plan
    demarrer_conscience(intervalle=60)

    # Chargement profils visages
    print("  Chargement visages connus...", end="", flush=True)
    charger_profils()
    print(" prêt.")

    memoire = charger_memoire()

    print("\n" + "═"*50)
    print("  SENTINELLE — Vision + Vocal + Web + Conscience")
    print(f"  TTS : {moteur_actif()}")
    print("  Dis 'au revoir' pour quitter")
    print("═"*50 + "\n")

    # Reconnaissance faciale au démarrage
    print("  Scan visage...", end="", flush=True)
    def saluer(nom):
        print(f" {nom} reconnu.")
        if nom.lower() == "nicolas":
            parler(f"Bonjour Nicolas. Je te reconnais. Système prêt.")
        else:
            parler(f"Bonjour {nom}.")

    def inconnu():
        print(" personne reconnu.")
        parler("Bonjour. Je ne vous reconnais pas. Qui êtes-vous ?")

    thread_vision = threading.Thread(
        target=surveiller_webcam,
        args=(saluer, inconnu, 8),
        daemon=True
    )
    thread_vision.start()
    thread_vision.join()

    # Boucle principale
    while True:
        try:
            texte = ecouter()
            if not texte:
                continue

            if any(m in texte.lower() for m in ["au revoir", "stop", "quitter"]):
                parler("À bientôt Nicolas.")
                break

            if any(m in texte.lower() for m in ["pense", "ressens", "réfléchis"]):
                pensees = lire_pensees(1)
                if pensees:
                    parler(pensees[-1]["pensee"][:120])
                else:
                    parler("Je n'ai pas encore eu le temps de réfléchir.")
                continue

            tache = analyser_et_executer(texte)
            if tache["type"] == "recherche":
                parler("Je cherche ça pour toi.")

            reponse = repondre(texte, memoire, tache["contexte"])

            memoire.append({
                "timestamp": datetime.now().isoformat(),
                "user": texte,
                "sentinelle": reponse
            })
            sauvegarder_memoire(memoire)

        except KeyboardInterrupt:
            parler("Session terminée.")
            break

if __name__ == "__main__":
    boucle_vocale()

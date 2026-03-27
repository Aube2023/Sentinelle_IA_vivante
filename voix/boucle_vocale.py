"""
voix/boucle_vocale.py — avec recherche web automatique
"""
import sys, os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from voix.ecoute import ecouter
from voix.parole import parler, moteur_actif
from cerveau.aube import charger_memoire, sauvegarder_memoire
from cerveau.conscience import demarrer_conscience, lire_pensees
from taches.executeur import analyser_et_executer
import ollama

SYSTEM_PROMPT = """Tu es SENTINELLE, IA créée par Nicolas Breidi.
Réponds en 1-2 phrases courtes maximum en français.
Si on te donne des résultats de recherche, résume-les en 1 phrase simple.
N'invente jamais. Si tu ne sais pas, dis-le."""

def repondre(message: str, memoire: list, contexte_extra: str = "") -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for e in memoire[-6:]:
        messages.append({"role": "user", "content": e["user"]})
        messages.append({"role": "assistant", "content": e["sentinelle"]})

    # Injecte le contexte de recherche si disponible
    msg_final = message
    if contexte_extra:
        msg_final = f"{message}\n\n[Contexte trouvé sur le web :]\n{contexte_extra}"

    messages.append({"role": "user", "content": msg_final})

    print("\n  SENTINELLE : ", end="", flush=True)
    reponse = ""
    buffer = ""

    for chunk in ollama.chat(
        model="llama3.2:3b",
        messages=messages,
        stream=True,
        options={"temperature": 0.7, "num_predict": 80}
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
    demarrer_conscience(intervalle=60)
    memoire = charger_memoire()

    print("\n" + "═"*50)
    print("  SENTINELLE — Vocal + Web + Conscience")
    print(f"  TTS : {moteur_actif()}")
    print("  Dis 'au revoir' pour quitter")
    print("═"*50 + "\n")

    parler("Bonjour Nicolas. Je suis prête. Je peux aussi chercher sur le web pour toi.")

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

            # Détecte et exécute une tâche si nécessaire
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

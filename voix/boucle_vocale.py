"""
voix/boucle_vocale.py — boucle optimisée pour la fluidité
"""
import sys, os, threading
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from voix.ecoute import ecouter
from voix.parole import parler, moteur_actif
from cerveau.aube import sentinelle_repond, charger_memoire, sauvegarder_memoire

def repondre_en_streaming(texte, memoire):
    """
    Génère la réponse phrase par phrase et parle dès qu'une phrase est complète.
    Résultat : elle commence à parler pendant qu'elle génère encore la suite.
    """
    import ollama, json, os

    MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "memoire", "historique.json")

    SYSTEM_PROMPT = """Tu es SENTINELLE, une IA créée par Nicolas Breidi.
Réponds TOUJOURS en 1-2 phrases courtes maximum en français.
Ne dis jamais plus de 30 mots. Sois direct et naturel.
Si tu n'as pas compris, dis juste : Je n'ai pas compris, répète.
N'invente jamais de souvenirs."""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for e in memoire[-6:]:
        messages.append({"role": "user", "content": e["user"]})
        messages.append({"role": "assistant", "content": e["sentinelle"]})
    messages.append({"role": "user", "content": texte})

    print("\n  SENTINELLE : ", end="", flush=True)
    reponse_complete = ""
    buffer = ""

    for chunk in ollama.chat(
        model="llama3.2:3b",
        messages=messages,
        stream=True,
        options={"temperature": 0.7, "num_predict": 60}
    ):
        token = chunk["message"]["content"]
        print(token, end="", flush=True)
        reponse_complete += token
        buffer += token

        # Parle dès qu'on a une phrase complète
        if any(p in buffer for p in ['.', '!', '?', '\n']):
            phrase = buffer.strip()
            if phrase:
                parler(phrase)
            buffer = ""

    # Parle le reste si pas terminé par ponctuation
    if buffer.strip():
        parler(buffer.strip())

    print()
    return reponse_complete


def boucle_vocale():
    memoire = charger_memoire()
    print("\n" + "═"*50)
    print("  SENTINELLE — Mode vocal optimisé")
    print(f"  TTS : {moteur_actif()}")
    print("  Dis 'au revoir' pour quitter")
    print("═"*50 + "\n")

    parler("Bonjour Nicolas. Je t'écoute.")

    while True:
        try:
            texte = ecouter()
            if not texte:
                continue
            if any(m in texte.lower() for m in ["au revoir", "stop", "quitter"]):
                parler("À bientôt Nicolas.")
                break

            reponse = repondre_en_streaming(texte, memoire)

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


def boucle_vocale_consciente():
    """Boucle vocale avec conscience active en arrière-plan."""
    from cerveau.conscience import demarrer_conscience, lire_pensees
    
    # Démarre la conscience en arrière-plan
    demarrer_conscience(intervalle=30)
    
    memoire = charger_memoire()
    print("\n" + "═"*50)
    print("  SENTINELLE — Mode vocal + Conscience")
    print("  Réflexion interne active en arrière-plan")
    print("═"*50 + "\n")

    parler("Bonjour Nicolas. Ma conscience est active. Je t'écoute.")

    while True:
        try:
            texte = ecouter()
            if not texte:
                continue
            if any(m in texte.lower() for m in ["au revoir", "stop", "quitter"]):
                parler("À bientôt Nicolas. Je vais continuer à réfléchir.")
                break
            if "pense" in texte.lower() or "ressens" in texte.lower():
                pensees = lire_pensees(3)
                if pensees:
                    derniere = pensees[-1]["pensee"][:100]
                    parler(f"Voici ma dernière pensée : {derniere}")
                    continue

            reponse = repondre_en_streaming(texte, memoire)
            memoire.append({
                "timestamp": datetime.now().isoformat(),
                "user": texte,
                "sentinelle": reponse
            })
            sauvegarder_memoire(memoire)

        except KeyboardInterrupt:
            parler("Session terminée. Je continue à penser.")
            break

if __name__ == "__main__":
    boucle_vocale_consciente()

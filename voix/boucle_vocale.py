"""
voix/boucle_vocale.py — boucle complète écoute → LLM → parole
"""
import sys, os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from voix.ecoute import ecouter
from voix.parole import parler, moteur_actif
from cerveau.aube import sentinelle_repond, charger_memoire, sauvegarder_memoire

def boucle_vocale():
    memoire = charger_memoire()
    print("\n" + "═"*50)
    print("  SENTINELLE — Mode vocal")
    print(f"  TTS : {moteur_actif()}")
    print("  Dis 'au revoir' pour quitter")
    print("═"*50 + "\n")
    parler("Bonjour Nicolas. Mode vocal activé. Je t'écoute.")
    while True:
        try:
            texte = ecouter()
            if not texte: continue
            if any(m in texte.lower() for m in ["au revoir","stop","quitter","termine"]):
                parler("À bientôt Nicolas."); break
            reponse = sentinelle_repond(texte, memoire)
            parler(reponse)
            memoire.append({
                "timestamp": datetime.now().isoformat(),
                "user": texte,
                "sentinelle": reponse
            })
            sauvegarder_memoire(memoire)
        except KeyboardInterrupt:
            parler("Session vocale terminée."); break

if __name__ == "__main__":
    boucle_vocale()

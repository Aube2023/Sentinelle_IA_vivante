"""
voix/parole.py — Sentinelle IA Vivante
Utilise uniquement say de macOS — simple et fiable
"""
import os
import subprocess

def parler(texte: str):
    if not texte or not texte.strip():
        return
    print(f"  SENTINELLE : {texte[:80]}{'...' if len(texte)>80 else ''}")
    # Nettoie le texte pour say
    texte_propre = texte.replace('"', '').replace("'", '').replace('\n', ' ')
    subprocess.run(['say', '-v', 'Thomas', '-r', '180', texte_propre])

def moteur_actif():
    return "macos"

if __name__ == "__main__":
    print(f"Moteur : {moteur_actif()}\n")
    parler("Bonjour Nicolas. Je suis Sentinelle. Tout système opérationnel.")

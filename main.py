"""
main.py — Sentinelle IA Vivante
"""
import os, sys

def check_ollama():
    try:
        import ollama; ollama.list(); return True
    except: return False

def check_module(nom):
    try:
        __import__(nom); return True
    except ImportError: return False

def main():
    print("\n" + "═"*55)
    print("  SENTINELLE — IA Vivante")
    print("  L'Aube Étoilée Technologies Drones Inc.")
    print("  Créée par Nicolas Breidi")
    print("═"*55 + "\n")

    modules = {
        "cerveau (Ollama)":   check_ollama(),
        "voix (Whisper)":     check_module("whisper"),
        "vision (webcam)":    check_module("cv2"),
        "tâches (pyautogui)": check_module("pyautogui"),
    }
    for nom, ok in modules.items():
        print(f"  {'✅' if ok else '⚠️ '} {nom}")

    print()
    if not modules["cerveau (Ollama)"]:
        print("  ERREUR : Ollama n'est pas actif.")
        print("  Lance : ollama serve  (dans un autre terminal)\n")
        sys.exit(1)

    from cerveau.aube import main as lancer
    lancer()

if __name__ == "__main__":
    main()

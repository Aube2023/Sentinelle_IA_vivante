"""
voix/parole.py — Sentinelle IA Vivante
"""
import os, sys

def _detecter_moteur():
    try:
        from TTS.api import TTS; return "coqui"
    except ImportError: pass
    try:
        import pyttsx3; return "pyttsx3"
    except ImportError: pass
    if sys.platform == "darwin": return "macos"
    return None

MOTEUR = _detecter_moteur()
_engine_pyttsx3 = None
_engine_coqui = None

def _parler_macos(texte, voix="Thomas"):
    os.system(f'say -v "{voix}" "{texte}"')

def _parler_pyttsx3(texte):
    global _engine_pyttsx3
    import pyttsx3
    if _engine_pyttsx3 is None:
        _engine_pyttsx3 = pyttsx3.init()
        _engine_pyttsx3.setProperty("rate", 170)
        for v in _engine_pyttsx3.getProperty("voices"):
            if "fr" in v.id.lower():
                _engine_pyttsx3.setProperty("voice", v.id); break
    _engine_pyttsx3.say(texte); _engine_pyttsx3.runAndWait()

def _parler_coqui(texte):
    global _engine_coqui
    from TTS.api import TTS
    import tempfile, subprocess
    if _engine_coqui is None:
        print("  Chargement Coqui TTS...", end="", flush=True)
        _engine_coqui = TTS("tts_models/fr/css10/vits"); print(" prêt.")
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    _engine_coqui.tts_to_file(text=texte, file_path=tmp.name)
    subprocess.run(["afplay", tmp.name]); os.unlink(tmp.name)

def parler(texte):
    if not texte or not texte.strip(): return
    print(f"  SENTINELLE : {texte[:60]}{'...' if len(texte)>60 else ''}")
    if MOTEUR == "coqui": _parler_coqui(texte)
    elif MOTEUR == "pyttsx3": _parler_pyttsx3(texte)
    elif MOTEUR == "macos": _parler_macos(texte)
    else: print("  [pip install pyttsx3]")

def moteur_actif(): return MOTEUR or "aucun"

if __name__ == "__main__":
    print(f"Moteur : {moteur_actif()}\n")
    parler("Bonjour Nicolas. Je suis Sentinelle. Tout système opérationnel.")

"""
voix/ecoute.py — Sentinelle IA Vivante
"""
import whisper, pyaudio, wave, tempfile, os

MODELE_WHISPER = "small"
RATE, CHANNELS, CHUNK = 16000, 1, 1024
FORMAT = pyaudio.paInt16
DUREE_SEC = 5
_modele = None

def charger_modele():
    global _modele
    if _modele is None:
        print("  Chargement Whisper... ", end="", flush=True)
        _modele = whisper.load_model(MODELE_WHISPER)
        print("prêt.")
    return _modele

def enregistrer_audio(duree=DUREE_SEC):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print(f"  Écoute... ({duree}s)", end="", flush=True)
    frames = [stream.read(CHUNK) for _ in range(int(RATE / CHUNK * duree))]
    print(" ✓")
    stream.stop_stream(); stream.close(); p.terminate()
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wf = wave.open(tmp.name, "wb")
    wf.setnchannels(CHANNELS); wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE); wf.writeframes(b"".join(frames)); wf.close()
    return tmp.name

def transcrire(fichier):
    modele = charger_modele()
    r = modele.transcribe(fichier, language="fr", fp16=False, verbose=False)
    os.unlink(fichier)
    return r["text"].strip()

def ecouter():
    texte = transcrire(enregistrer_audio())
    if texte: print(f"  Nicolas (voix) : {texte}")
    return texte

if __name__ == "__main__":
    print("Test écoute — parle pendant 5 secondes\n")
    print(f"Transcription : '{ecouter()}'")

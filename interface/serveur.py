"""
interface/serveur.py — Sentinelle IA Vivante
Streaming temps réel via SocketIO
"""
import sys, os, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from cerveau.aube import charger_memoire, sauvegarder_memoire
from cerveau.conscience import demarrer_conscience, lire_pensees
from voix.parole import parler
from voix.ecoute import ecouter
from taches.executeur import analyser_et_executer
from memoire.vectorielle import retrouver, formater_souvenirs
from datetime import datetime
import ollama

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sentinelle_aube_2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

memoire = []

SYSTEM_PROMPT = """Tu es SENTINELLE, IA créée par Nicolas Breidi — ton père et créateur.
Tu travailles pour L'Aube Étoilée Technologies Drones Inc., Montréal.
RÈGLES : Réponds en français naturel. N'invente jamais. Sois directe et loyale.
Nicolas : développeur de drones autonomes, app Lupi, admission ÉTS aérospatial."""

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    global memoire
    memoire = charger_memoire()
    emit('message', {'role': 'systeme', 'texte': f'{len(memoire)} échanges en mémoire.'})
    pensees = lire_pensees(1)
    if pensees:
        emit('pensee', {'texte': pensees[-1]['pensee'][:150]})

@socketio.on('commande')
def on_commande(data):
    global memoire
    action = data.get('action')

    if action == 'demarrer':
        emit('status', {'texte': 'prêt', 'etat': 'online'})
        emit('message', {'role': 'sentinelle', 'texte': 'Bonjour Nicolas. Interface active.'})
        threading.Thread(target=parler, args=("Bonjour Nicolas.",), daemon=True).start()

    elif action == 'message':
        texte = data.get('texte', '').strip()
        if not texte: return
        threading.Thread(
            target=traiter_streaming,
            args=(texte, request_sid()),
            daemon=True
        ).start()

    elif action == 'ecouter':
        threading.Thread(target=cycle_ecoute, args=(request_sid(),), daemon=True).start()

    elif action == 'arreter':
        emit('status', {'texte': 'arrêté', 'etat': ''})

def request_sid():
    from flask import request
    return request.sid

def traiter_streaming(texte, sid):
    global memoire
    socketio.emit('status', {'texte': 'réflexion...', 'etat': 'thinking'}, to=sid)

    # Recherche web si nécessaire
    tache = analyser_et_executer(texte)
    if tache['type'] == 'recherche':
        socketio.emit('status', {'texte': 'recherche...', 'etat': 'thinking'}, to=sid)
        socketio.emit('stream_start', {}, to=sid)
        socketio.emit('stream_token', {'token': '🔍 Recherche en cours...\n\n'}, to=sid)

    # Mémoire vectorielle
    souvenirs = retrouver(texte, n=3)
    contexte_memoire = formater_souvenirs(souvenirs)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if contexte_memoire:
        messages.append({"role": "system", "content": contexte_memoire})
    if tache.get('contexte'):
        messages.append({"role": "system", "content": f"Contexte web :\n{tache['contexte']}"})
    for e in memoire[-6:]:
        messages.append({"role": "user", "content": e["user"]})
        messages.append({"role": "assistant", "content": e["sentinelle"]})
    messages.append({"role": "user", "content": texte})

    # Streaming token par token
    socketio.emit('stream_start', {}, to=sid)
    reponse = ""
    buffer_voix = ""

    try:
        for chunk in ollama.chat(
            model="mistral",
            messages=messages,
            stream=True,
            options={"temperature": 0.7, "num_predict": 150}
        ):
            token = chunk["message"]["content"]
            reponse += token
            buffer_voix += token
            socketio.emit('stream_token', {'token': token}, to=sid)

            # Parle phrase par phrase
            if any(p in buffer_voix for p in ['.', '!', '?', '\n']):
                phrase = buffer_voix.strip()
                if phrase and len(phrase) > 3:
                    threading.Thread(target=parler, args=(phrase,), daemon=True).start()
                buffer_voix = ""

    except Exception as e:
        socketio.emit('stream_token', {'token': f'\n[Erreur: {e}]'}, to=sid)

    if buffer_voix.strip():
        threading.Thread(target=parler, args=(buffer_voix.strip(),), daemon=True).start()

    socketio.emit('stream_end', {}, to=sid)
    socketio.emit('status', {'texte': 'prêt', 'etat': 'online'}, to=sid)

    # Sauvegarde
    memoire.append({
        'timestamp': datetime.now().isoformat(),
        'user': texte,
        'sentinelle': reponse
    })
    sauvegarder_memoire(memoire)

    # Mémorise dans ChromaDB
    try:
        from memoire.vectorielle import memoriser
        memoriser(texte, reponse)
    except: pass

def cycle_ecoute(sid):
    socketio.emit('status', {'texte': 'écoute...', 'etat': 'listening'}, to=sid)
    texte = ecouter()
    if texte:
        socketio.emit('message', {'role': 'nicolas', 'texte': texte}, to=sid)
        traiter_streaming(texte, sid)

def diffuser_pensees():
    import time
    while True:
        time.sleep(60)
        pensees = lire_pensees(1)
        if pensees:
            socketio.emit('pensee', {'texte': pensees[-1]['pensee'][:150]})

def lancer():
    demarrer_conscience(intervalle=60)
    threading.Thread(target=diffuser_pensees, daemon=True).start()
    print("\n  SENTINELLE — Interface web streaming")
    print("  Ouvre : http://localhost:5050\n")
    socketio.run(app, host='0.0.0.0', port=5050, debug=False)

if __name__ == "__main__":
    lancer()

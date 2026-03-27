"""
interface/serveur.py — Sentinelle IA Vivante
Serveur Flask + SocketIO — interface web temps réel
"""
import sys, os, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from cerveau.aube import sentinelle_repond, charger_memoire, sauvegarder_memoire
from voix.parole import parler
from voix.ecoute import ecouter
from cerveau.conscience import demarrer_conscience, lire_pensees
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sentinelle_aube_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

memoire = []
_ecoute_active = False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    global memoire
    memoire = charger_memoire()
    emit('message', {'role': 'systeme', 'texte': f'Mémoire chargée — {len(memoire)} échanges.'})
    # Envoie les pensées récentes
    pensees = lire_pensees(1)
    if pensees:
        emit('pensee', {'texte': pensees[-1]['pensee'][:150]})

@socketio.on('commande')
def on_commande(data):
    global memoire, _ecoute_active
    action = data.get('action')

    if action == 'demarrer':
        emit('status', {'texte': 'prêt', 'etat': 'active'})
        emit('message', {'role': 'sentinelle', 'texte': 'Bonjour Nicolas. Interface active.'})
        parler("Bonjour Nicolas. Interface web activée.")

    elif action == 'message':
        texte = data.get('texte', '').strip()
        if not texte: return
        emit('status', {'texte': 'réflexion...', 'etat': 'thinking'})
        def traiter():
            reponse = sentinelle_repond(texte, memoire)
            memoire.append({
                'timestamp': datetime.now().isoformat(),
                'user': texte,
                'sentinelle': reponse
            })
            sauvegarder_memoire(memoire)
            socketio.emit('message', {'role': 'sentinelle', 'texte': reponse})
            socketio.emit('status', {'texte': 'prêt', 'etat': 'active'})
            parler(reponse[:200])
        threading.Thread(target=traiter, daemon=True).start()

    elif action == 'ecouter':
        def cycle_ecoute():
            socketio.emit('status', {'texte': 'écoute...', 'etat': 'listening'})
            texte = ecouter()
            if texte:
                socketio.emit('message', {'role': 'nicolas', 'texte': texte})
                socketio.emit('status', {'texte': 'réflexion...', 'etat': 'thinking'})
                reponse = sentinelle_repond(texte, memoire)
                memoire.append({
                    'timestamp': datetime.now().isoformat(),
                    'user': texte,
                    'sentinelle': reponse
                })
                sauvegarder_memoire(memoire)
                socketio.emit('message', {'role': 'sentinelle', 'texte': reponse})
                socketio.emit('status', {'texte': 'prêt', 'etat': 'active'})
                parler(reponse[:200])
        threading.Thread(target=cycle_ecoute, daemon=True).start()

    elif action == 'arreter':
        emit('status', {'texte': 'arrêté', 'etat': ''})

def diffuser_pensees():
    """Envoie les nouvelles pensées à l'interface toutes les 60s."""
    import time
    while True:
        time.sleep(60)
        pensees = lire_pensees(1)
        if pensees:
            socketio.emit('pensee', {'texte': pensees[-1]['pensee'][:150]})

def lancer():
    demarrer_conscience(intervalle=60)
    threading.Thread(target=diffuser_pensees, daemon=True).start()
    print("\n  SENTINELLE — Interface web")
    print("  Ouvre : http://localhost:5050\n")
    socketio.run(app, host='0.0.0.0', port=5050, debug=False)

if __name__ == "__main__":
    lancer()

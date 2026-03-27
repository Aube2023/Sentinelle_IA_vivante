import sys, os, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from cerveau.aube import charger_memoire, sauvegarder_memoire
from datetime import datetime
import ollama

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sentinelle'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
memoire = []

SYSTEM_PROMPT = """Tu es SENTINELLE, IA créée par Nicolas Breidi pour L'Aube Étoilée.
Réponds en français naturel. Sois complète et précise. N'invente jamais."""

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    global memoire
    memoire = charger_memoire()
    emit('message', {'role':'systeme','texte':f'Sentinelle prête — {len(memoire)} échanges.'})

@socketio.on('commande')
def on_commande(data):
    action = data.get('action')
    if action == 'demarrer':
        emit('status', {'texte':'prêt','etat':'online'})
        emit('message', {'role':'sentinelle','texte':'Bonjour Nicolas.'})
    elif action == 'message':
        texte = data.get('texte','').strip()
        if not texte: return
        sid = request.sid
        threading.Thread(target=repondre, args=(texte, sid), daemon=True).start()
    elif action == 'arreter':
        emit('status', {'texte':'arrêté','etat':''})

def repondre(texte, sid):
    global memoire
    socketio.emit('status', {'texte':'réflexion...','etat':'thinking'}, to=sid)

    messages = [{"role":"system","content":SYSTEM_PROMPT}]
    for e in memoire[-6:]:
        messages.append({"role":"user","content":e["user"]})
        messages.append({"role":"assistant","content":e["sentinelle"]})
    messages.append({"role":"user","content":texte})

    reponse = ""
    try:
        result = ollama.chat(
            model="phi3:mini",
            messages=messages,
            options={"temperature":0.7,"num_predict":300}
        )
        reponse = result["message"]["content"]
    except Exception as e:
        reponse = f"Erreur: {e}"

    socketio.emit('message', {'role':'sentinelle','texte':reponse}, to=sid)
    socketio.emit('status', {'texte':'prêt','etat':'online'}, to=sid)

    memoire.append({'timestamp':datetime.now().isoformat(),'user':texte,'sentinelle':reponse})
    sauvegarder_memoire(memoire)

if __name__ == "__main__":
    print("\n  SENTINELLE LIGHT — http://localhost:5050\n")
    socketio.run(app, host='0.0.0.0', port=5050, debug=False)

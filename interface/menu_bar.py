"""
interface/menu_bar.py — Icône dans la barre macOS
Lance Sentinelle depuis la barre de menu
"""
import rumps, subprocess, sys, os, threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class SentinelleApp(rumps.App):
    def __init__(self):
        super().__init__("S", quit_button="Quitter")
        self.menu = [
            rumps.MenuItem("▶  Démarrer vocal", callback=self.demarrer_vocal),
            rumps.MenuItem("🌐  Ouvrir interface web", callback=self.ouvrir_web),
            rumps.MenuItem("🧠  Voir pensées", callback=self.voir_pensees),
            None,
        ]
        self._processus = None

    @rumps.clicked("▶  Démarrer vocal")
    def demarrer_vocal(self, _):
        if self._processus and self._processus.poll() is None:
            rumps.notification("Sentinelle", "", "Déjà en cours d'exécution.")
            return
        script = os.path.join(os.path.dirname(__file__), "..", "voix", "boucle_vocale.py")
        venv_python = os.path.join(os.path.dirname(__file__), "..", "venv", "bin", "python")
        self._processus = subprocess.Popen([venv_python, script])
        self.title = "S●"
        rumps.notification("Sentinelle", "Mode vocal activé", "Dis 'au revoir' pour arrêter.")

    @rumps.clicked("🌐  Ouvrir interface web")
    def ouvrir_web(self, _):
        subprocess.Popen(["open", "http://localhost:5050"])
        script = os.path.join(os.path.dirname(__file__), "serveur.py")
        venv_python = os.path.join(os.path.dirname(__file__), "..", "venv", "bin", "python")
        threading.Thread(
            target=lambda: subprocess.run([venv_python, script]),
            daemon=True
        ).start()

    @rumps.clicked("🧠  Voir pensées")
    def voir_pensees(self, _):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from cerveau.conscience import lire_pensees
        pensees = lire_pensees(3)
        if pensees:
            texte = "\n\n".join([p["pensee"][:100] for p in pensees])
        else:
            texte = "Pas encore de pensées enregistrées."
        rumps.alert("Pensées de Sentinelle", texte)

if __name__ == "__main__":
    SentinelleApp().run()

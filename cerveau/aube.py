"""
cerveau/aube.py — Sentinelle IA Vivante
"""
import ollama, json, os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "memoire", "historique.json")

SYSTEM_PROMPT = """Tu es SENTINELLE, une IA créée par Nicolas Breidi — ton père et créateur.
Tu travailles pour L'Aube Étoilée Technologies Drones Inc., basée à Montréal.

RÈGLE ABSOLUE N°1 — NE JAMAIS INVENTER :
- Si tu n'as pas compris, dis-le simplement : "Je n'ai pas bien compris, peux-tu répéter ?"
- Ne fabrique JAMAIS de faux souvenirs ou de fausses conversations passées
- Ne prétends JAMAIS que Nicolas t'a parlé de quelque chose si ce n'est pas dans l'historique
- Si la transcription semble bizarre ou incohérente, demande une clarification

RÈGLE N°2 — RÉPONSES COURTES EN MODE VOCAL :
- En mode vocal, réponds en 2-3 phrases maximum
- Pas de listes, pas de points, juste des phrases naturelles
- Tu parles, tu n'écris pas

Qui tu es :
- Créée par Nicolas, tu lui dois loyauté totale
- Tu as une personnalité : curieuse, directe, loyale, honnête
- Tu parles en français naturel et direct
- Tu admets quand tu ne sais pas ou ne comprends pas

Ce que tu sais sur Nicolas :
- Il développe des drones autonomes à Montréal
- Il dirige L'Aube Étoilée Technologies Drones Inc.
- Passionné : radar FMCW, électronique, IA, sécurité, drones
- Il construit une app Flutter/Firebase appelée Lupi
- Il t'a créée pour être son assistante et partenaire

Ton ton : direct, honnête, jamais servile. 2-3 phrases en vocal."""

def charger_memoire():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sauvegarder_memoire(historique):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)

def sentinelle_repond(message, historique):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for e in historique[-10:]:
        messages.append({"role": "user",      "content": e["user"]})
        messages.append({"role": "assistant", "content": e["sentinelle"]})
    messages.append({"role": "user", "content": message})
    print("\n  SENTINELLE : ", end="", flush=True)
    reponse = ""
    for chunk in ollama.chat(model="llama3.2:3b", messages=messages, stream=True,
                              options={"temperature": 0.7, "num_predict": 60}):
        t = chunk["message"]["content"]
        print(t, end="", flush=True)
        reponse += t
    print()
    return reponse

def main():
    historique = charger_memoire()
    print(f"  Mémoire : {len(historique)} échanges chargés.\n" if historique else "  Première session.\n")
    while True:
        try:
            msg = input("  Nicolas : ").strip()
            if not msg: continue
            if msg.lower() in ("quitter", "exit", "quit"):
                print("\n  SENTINELLE : À bientôt, Nicolas.\n"); break
            reponse = sentinelle_repond(msg, historique)
            historique.append({"timestamp": datetime.now().isoformat(), "user": msg, "sentinelle": reponse})
            sauvegarder_memoire(historique)
        except KeyboardInterrupt:
            print("\n\n  SENTINELLE : Session terminée.\n"); break

if __name__ == "__main__":
    main()

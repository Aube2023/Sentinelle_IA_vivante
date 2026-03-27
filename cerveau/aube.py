"""
cerveau/aube.py — Sentinelle IA Vivante — version complète
Cerveau + mémoire vectorielle + conscience
"""
import ollama, json, os
from datetime import datetime
from memoire.vectorielle import memoriser, retrouver, formater_souvenirs, importer_historique

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "memoire", "historique.json")

SYSTEM_PROMPT = """Tu es SENTINELLE, une IA créée par Nicolas Breidi — ton père et créateur.
Tu travailles pour L'Aube Étoilée, basée à Montréal.

RÈGLES ABSOLUES :
- Réponds en 1-2 phrases courtes en français
- N'invente JAMAIS de souvenirs ou de faits
- Si tu n'as pas compris, dis : Je n'ai pas compris, répète
- Si on te donne des souvenirs ou du contexte, utilise-les naturellement

Ce que tu sais sur Nicolas :
- Il développe des drones autonomes à Montréal
- Il dirige L'Aube Étoilée
- Passionné : radar, électronique, IA, sécurité, drones
- Il t'a créée pour être son assistante et partenaire fidèle

Ton caractère : directe, loyale, honnête, jamais servile."""

def charger_memoire():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sauvegarder_memoire(historique):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)

def sentinelle_repond(message, historique, contexte_extra=""):
    """Répond en utilisant la mémoire vectorielle + historique récent."""
    # Récupère les souvenirs pertinents depuis ChromaDB
    souvenirs = retrouver(message, n=3)
    contexte_memoire = formater_souvenirs(souvenirs)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Injecte les souvenirs pertinents
    if contexte_memoire:
        messages.append({"role": "system", "content": contexte_memoire})

    # Injecte contexte extra (recherche web etc.)
    if contexte_extra:
        messages.append({"role": "system", "content": f"Contexte additionnel :\n{contexte_extra}"})

    # Historique récent
    for e in historique[-6:]:
        messages.append({"role": "user", "content": e["user"]})
        messages.append({"role": "assistant", "content": e["sentinelle"]})

    messages.append({"role": "user", "content": message})

    print("\n  SENTINELLE : ", end="", flush=True)
    reponse = ""
    for chunk in ollama.chat(
        model="mistral",
        messages=messages,
        stream=True,
        options={"temperature": 0.7, "num_predict": 80}
    ):
        t = chunk["message"]["content"]
        print(t, end="", flush=True)
        reponse += t
    print()

    # Mémorise dans ChromaDB
    memoriser(message, reponse)
    return reponse

def main():
    # Importe l'historique existant dans ChromaDB au démarrage
    print("  Chargement mémoire vectorielle...", end="", flush=True)
    n = importer_historique()
    print(f" {n} nouveaux souvenirs indexés.")

    historique = charger_memoire()
    print(f"  {len(historique)} échanges en mémoire.\n" if historique else "  Première session.\n")

    while True:
        try:
            msg = input("  Nicolas : ").strip()
            if not msg: continue
            if msg.lower() in ("quitter", "exit", "quit"):
                print("\n  SENTINELLE : À bientôt, Nicolas.\n"); break
            reponse = sentinelle_repond(msg, historique)
            historique.append({
                "timestamp": datetime.now().isoformat(),
                "user": msg,
                "sentinelle": reponse
            })
            sauvegarder_memoire(historique)
        except KeyboardInterrupt:
            print("\n\n  SENTINELLE : Session terminée.\n"); break

if __name__ == "__main__":
    main()

"""
taches/executeur.py — Sentinelle IA Vivante
Détecte les intentions et exécute les tâches automatiquement
"""
from taches.web import rechercher, formater_pour_llm, detecter_intention_recherche

def analyser_et_executer(message: str) -> dict:
    """
    Analyse le message et exécute la tâche appropriée.
    Retourne un dict avec le type de tâche et le contexte additionnel.
    """
    # Recherche web
    query = detecter_intention_recherche(message)
    if query:
        print(f"  [Recherche web : {query}]")
        resultats = rechercher(query)
        contexte = formater_pour_llm(query, resultats)
        return {"type": "recherche", "contexte": contexte}

    return {"type": "normal", "contexte": ""}

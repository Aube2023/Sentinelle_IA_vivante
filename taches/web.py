"""
taches/web.py — Sentinelle IA Vivante
Recherche web automatique via DuckDuckGo (sans API key)
"""
import requests, json, re

def rechercher(query: str, max_resultats: int = 3) -> list:
    """
    Recherche sur DuckDuckGo et retourne les résultats.
    Pas besoin de clé API.
    """
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        r = requests.get(url, params=params, timeout=5)
        data = r.json()

        resultats = []

        # Réponse directe (définition, fait)
        if data.get("AbstractText"):
            resultats.append({
                "titre": data.get("Heading", ""),
                "texte": data["AbstractText"][:300],
                "url": data.get("AbstractURL", "")
            })

        # Résultats connexes
        for item in data.get("RelatedTopics", [])[:max_resultats]:
            if isinstance(item, dict) and item.get("Text"):
                resultats.append({
                    "titre": item.get("Text", "")[:80],
                    "texte": item.get("Text", "")[:200],
                    "url": item.get("FirstURL", "")
                })

        return resultats[:max_resultats]

    except Exception as e:
        return [{"titre": "Erreur", "texte": str(e), "url": ""}]


def formater_pour_llm(query: str, resultats: list) -> str:
    """Formate les résultats pour que le LLM puisse les utiliser."""
    if not resultats:
        return f"Aucun résultat trouvé pour : {query}"

    texte = f"Résultats de recherche pour '{query}' :\n\n"
    for i, r in enumerate(resultats, 1):
        texte += f"{i}. {r['titre']}\n{r['texte']}\n\n"
    return texte


def detecter_intention_recherche(message: str) -> str | None:
    """
    Détecte si le message demande une recherche web.
    Retourne la query à chercher ou None.
    """
    declencheurs = [
        "cherche", "recherche", "trouve", "googler",
        "c'est quoi", "keskon", "qu'est-ce que",
        "info sur", "actualité", "news", "météo",
        "prix de", "comment faire", "qui est"
    ]
    msg_lower = message.lower()
    for d in declencheurs:
        if d in msg_lower:
            # Extrait la query — enlève le déclencheur
            query = msg_lower
            for mot in ["cherche", "recherche", "trouve", "dis-moi", "c'est quoi"]:
                query = query.replace(mot, "").strip()
            return query if len(query) > 2 else message
    return None


if __name__ == "__main__":
    print("Test recherche web\n")
    resultats = rechercher("drones autonomes Canada 2024")
    for r in resultats:
        print(f"• {r['titre']}")
        print(f"  {r['texte'][:100]}...")
        print()

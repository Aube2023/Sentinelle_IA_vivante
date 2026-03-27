"""
taches/web.py — Sentinelle IA Vivante
Recherche web via DuckDuckGo + extraction intelligente de query
"""
import requests, ollama

def extraire_query(message: str) -> str:
    """Utilise le LLM pour extraire la vraie query de recherche."""
    try:
        r = ollama.chat(
            model="llama3.2:3b",
            messages=[{"role": "user", "content":
                f"Extrait uniquement les mots-clés de recherche de cette phrase, sans mots inutiles, en 3-5 mots max. Réponds UNIQUEMENT avec les mots-clés, rien d'autre.\n\nPhrase: {message}"}],
            options={"temperature": 0.1, "num_predict": 20}
        )
        return r["message"]["content"].strip()
    except:
        return message

def rechercher(query: str, max_resultats: int = 3) -> list:
    """Recherche sur DuckDuckGo."""
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=5
        )
        data = r.json()
        resultats = []

        if data.get("AbstractText"):
            resultats.append({
                "titre": data.get("Heading", query),
                "texte": data["AbstractText"][:300]
            })

        for item in data.get("RelatedTopics", [])[:max_resultats]:
            if isinstance(item, dict) and item.get("Text"):
                resultats.append({
                    "titre": item.get("Text", "")[:60],
                    "texte": item.get("Text", "")[:200]
                })

        return resultats[:max_resultats]
    except Exception as e:
        return []

def formater_pour_llm(query: str, resultats: list) -> str:
    if not resultats:
        return f"Aucun résultat pour : {query}"
    texte = f"Résultats pour '{query}' :\n"
    for r in resultats:
        texte += f"- {r['texte']}\n"
    return texte

def detecter_intention_recherche(message: str) -> str | None:
    declencheurs = [
        "cherche", "recherche", "trouve", "googler",
        "c'est quoi", "qu'est-ce que", "info sur",
        "actualité", "news", "météo", "prix de",
        "qui est", "quoi de neuf"
    ]
    msg_lower = message.lower()
    for d in declencheurs:
        if d in msg_lower:
            return extraire_query(message)
    return None

if __name__ == "__main__":
    query = extraire_query("cherche des informations sur les drones autonomes au Canada")
    print(f"Query extraite : {query}")
    resultats = rechercher(query)
    print(formater_pour_llm(query, resultats))

"""
taches/web.py — recherche web avec ddgs
"""
import ollama
from ddgs import DDGS

def extraire_query(message: str) -> str:
    try:
        r = ollama.chat(
            model="llama3.2:3b",
            messages=[{"role": "user", "content":
                f"Donne uniquement 3-4 mots-clés en français pour rechercher : {message}. UNIQUEMENT les mots-clés."}],
            options={"temperature": 0.1, "num_predict": 15}
        )
        return r["message"]["content"].strip().replace("\n", " ")
    except:
        return message

def rechercher(query: str, max_resultats: int = 3) -> list:
    try:
        with DDGS() as ddgs:
            resultats = list(ddgs.text(
                query,
                max_results=max_resultats,
                region="ca-fr"
            ))
        return [{"titre": r.get("title",""), "texte": r.get("body","")[:250]} for r in resultats]
    except Exception as e:
        print(f"  [Erreur recherche : {e}]")
        return []

def formater_pour_llm(query: str, resultats: list) -> str:
    if not resultats:
        return f"Aucun résultat pour : {query}"
    texte = f"Résultats pour '{query}' :\n"
    for r in resultats:
        texte += f"- {r['titre']} : {r['texte']}\n"
    return texte

def detecter_intention_recherche(message: str) -> str | None:
    declencheurs = ["cherche", "recherche", "trouve", "googler",
                    "c'est quoi", "qu'est-ce que", "info sur",
                    "actualité", "news", "météo", "qui est", "quoi de neuf"]
    if any(d in message.lower() for d in declencheurs):
        return extraire_query(message)
    return None

if __name__ == "__main__":
    q = extraire_query("fais une recherche sur les drones autonomes")
    print(f"Query : {q}")
    r = rechercher(q)
    print(formater_pour_llm(q, r))

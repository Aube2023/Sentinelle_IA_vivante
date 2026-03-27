"""
memoire/vectorielle.py — Sentinelle IA Vivante
Mémoire longue durée avec ChromaDB
Elle se souvient de TOUT et retrouve les souvenirs pertinents par sens
"""
import chromadb, json, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "chromadb")

_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=DB_PATH)
        _collection = _client.get_or_create_collection(
            name="sentinelle_memoire",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

def memoriser(user: str, sentinelle: str, timestamp: str = None):
    """Stocke un échange dans la mémoire vectorielle."""
    col = get_collection()
    if not timestamp:
        timestamp = datetime.now().isoformat()
    doc_id = f"echange_{timestamp}"
    texte = f"Nicolas: {user}\nSentinelle: {sentinelle}"
    col.add(
        documents=[texte],
        metadatas=[{"timestamp": timestamp, "user": user, "sentinelle": sentinelle}],
        ids=[doc_id]
    )

def retrouver(question: str, n: int = 5) -> list:
    """
    Retrouve les N souvenirs les plus pertinents par rapport à la question.
    C'est ici que la magie opère — elle cherche par SENS, pas par mot-clé.
    """
    col = get_collection()
    if col.count() == 0:
        return []
    resultats = col.query(
        query_texts=[question],
        n_results=min(n, col.count())
    )
    souvenirs = []
    for i, doc in enumerate(resultats["documents"][0]):
        meta = resultats["metadatas"][0][i]
        souvenirs.append({
            "texte": doc,
            "timestamp": meta.get("timestamp", ""),
            "distance": resultats["distances"][0][i]
        })
    return souvenirs

def formater_souvenirs(souvenirs: list) -> str:
    """Formate les souvenirs pour le LLM."""
    if not souvenirs:
        return ""
    texte = "Souvenirs pertinents de conversations passées :\n"
    for s in souvenirs:
        date = s["timestamp"][:10] if s["timestamp"] else ""
        texte += f"[{date}] {s['texte'][:200]}\n\n"
    return texte

def importer_historique():
    """Importe l'historique JSON existant dans ChromaDB."""
    hist_file = os.path.join(os.path.dirname(__file__), "historique.json")
    if not os.path.exists(hist_file):
        return 0
    with open(hist_file, "r", encoding="utf-8") as f:
        historique = json.load(f)
    col = get_collection()
    importes = 0
    for e in historique:
        doc_id = f"echange_{e['timestamp']}"
        try:
            col.get(ids=[doc_id])
        except:
            memoriser(e["user"], e["sentinelle"], e["timestamp"])
            importes += 1
    return importes

if __name__ == "__main__":
    print("Import de l'historique existant...")
    n = importer_historique()
    print(f"{n} échanges importés.")
    col = get_collection()
    print(f"Total en mémoire : {col.count()} échanges\n")
    print("Test de recherche par sens...")
    souvenirs = retrouver("drones et reconnaissance faciale")
    print(formater_souvenirs(souvenirs))

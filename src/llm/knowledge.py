from pathlib import Path
import joblib
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_DIR = Path(__file__).resolve().parents[2]
INDEX_PATH = PROJECT_DIR / "rag" / "index" / "knowledge_index.joblib"
_CACHE = None

def _load_index():
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not INDEX_PATH.exists():
        return None
    _CACHE = joblib.load(INDEX_PATH)
    return _CACHE

def search_knowledge(query: str, top_k: int = 4):
    index = _load_index()
    if index is None:
        return {
            "status": "missing_index",
            "message": "Knowledge index is missing. Run: python -m scripts.build_knowledge_index",
            "results": [],
        }

    vectorizer = index["vectorizer"]
    matrix = index["matrix"]
    chunks = index["chunks"]
    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, matrix)[0]
    ranked_indexes = scores.argsort()[::-1]
    results = []

    for item_index in ranked_indexes:
        if len(results) >= top_k:
            break
        score = float(scores[item_index])
        if score <= 0:
            continue
        chunk = chunks[item_index]
        results.append({
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"],
            "score": round(score, 4),
            "text": chunk["text"],
        })

    return {"status": "ok", "results": results}

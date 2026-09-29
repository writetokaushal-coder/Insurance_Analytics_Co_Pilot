from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

PROJECT_DIR = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = PROJECT_DIR / "rag" / "knowledge"
INDEX_DIR = PROJECT_DIR / "rag" / "index"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

chunks = []
if KNOWLEDGE_DIR.exists():
    for path in KNOWLEDGE_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".txt", ".md"}:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        for index, paragraph in enumerate(paragraphs):
            chunks.append({
                "source": path.name,
                "chunk_id": str(index),
                "text": paragraph,
            })

if not chunks:
    raise RuntimeError("No .txt or .md files found in rag/knowledge.")

documents = [item["text"] for item in chunks]
vectorizer = TfidfVectorizer(stop_words="english")
matrix = vectorizer.fit_transform(documents)
output_path = INDEX_DIR / "knowledge_index.joblib"
joblib.dump({"chunks": chunks, "vectorizer": vectorizer, "matrix": matrix}, output_path)
print("Knowledge index built successfully.")
print("Chunks:", len(chunks))
print("Saved:", output_path)

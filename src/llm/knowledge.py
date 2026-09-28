from pathlib import Path

from sklearn.feature_extraction.text import (
    TfidfVectorizer
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)


PROJECT_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

KNOWLEDGE_DIR = (
    PROJECT_DIR
    / "rag"
    / "knowledge"
)


def _load_chunks():

    if not KNOWLEDGE_DIR.exists():
        return []


    chunks = []


    for path in KNOWLEDGE_DIR.rglob("*"):

        if (
            not path.is_file()
            or
            path.suffix.lower()
            not in {
                ".txt",
                ".md",
            }
        ):
            continue


        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )


        paragraphs = [
            paragraph.strip()
            for paragraph
            in text.split(
                "\n\n"
            )
            if paragraph.strip()
        ]


        for index, paragraph in enumerate(
            paragraphs
        ):

            # Keep retrieval units manageable.
            if len(paragraph) > 1800:

                for start in range(
                    0,
                    len(paragraph),
                    1500,
                ):

                    piece = paragraph[
                        start:
                        start + 1800
                    ].strip()

                    if piece:

                        chunks.append({
                            "source":
                                path.name,

                            "chunk_id":
                                f"{index}-{start}",

                            "text":
                                piece,
                        })

            else:

                chunks.append({
                    "source":
                        path.name,

                    "chunk_id":
                        str(index),

                    "text":
                        paragraph,
                })


    return chunks


def search_knowledge(
    query: str,
    top_k: int = 4,
):

    chunks = _load_chunks()


    if not chunks:

        return {
            "status":
                "empty",

            "message":
                (
                    "No .txt or .md knowledge files "
                    "were found in rag/knowledge."
                ),

            "results":
                [],
        }


    documents = [
        chunk[
            "text"
        ]
        for chunk in chunks
    ]


    vectorizer = (
        TfidfVectorizer(
            stop_words="english"
        )
    )


    matrix = vectorizer.fit_transform(
        documents
        +
        [
            query
        ]
    )


    scores = cosine_similarity(
        matrix[-1:],
        matrix[:-1],
    )[0]


    ranked_indexes = (
        scores.argsort()[::-1]
    )


    results = []


    for index in ranked_indexes:

        if len(results) >= top_k:
            break


        score = float(
            scores[
                index
            ]
        )


        if score <= 0:
            continue


        chunk = chunks[
            index
        ]


        results.append({
            "source":
                chunk[
                    "source"
                ],

            "chunk_id":
                chunk[
                    "chunk_id"
                ],

            "score":
                round(
                    score,
                    4
                ),

            "text":
                chunk[
                    "text"
                ],
        })


    return {
        "status":
            "ok",

        "results":
            results,
    }

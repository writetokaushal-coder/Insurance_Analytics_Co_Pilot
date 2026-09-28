from typing import Dict


def detect_intent(message: str) -> Dict[str, object]:
    """Lightweight deterministic intent router."""

    text = message.strip().lower()

    renewal_keywords = [
        "renew", "renewal", "non-renewal", "non renewal",
        "lapse", "retention",
    ]

    fraud_keywords = [
        "fraud", "fraudulent", "suspicious", "suspicion",
        "claim fraud", "fraud risk",
    ]

    underwriting_keywords = [
        "underwriting", "underwrite", "underwriter",
        "approve applicant", "decline applicant",
        "loading", "premium loading",
    ]

    scores = {
        "renewal": sum(keyword in text for keyword in renewal_keywords),
        "fraud": sum(keyword in text for keyword in fraud_keywords),
        "underwriting": sum(keyword in text for keyword in underwriting_keywords),
    }

    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]

    if best_score == 0:
        return {
            "intent": "general",
            "confidence": 0.0,
            "scores": scores,
        }

    tied = [
        intent
        for intent, score in scores.items()
        if score == best_score
    ]

    if len(tied) > 1:
        return {
            "intent": "clarification",
            "confidence": 0.5,
            "candidate_intents": tied,
            "scores": scores,
        }

    return {
        "intent": best_intent,
        "confidence": 1.0,
        "scores": scores,
    }

import os
import requests

DEFAULT_API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")

class InsuranceAPIClient:
    def __init__(self, base_url: str = DEFAULT_API_URL, timeout: int = 650):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = os.getenv("APP_API_KEY", "").strip()

    def _headers(self):
        return {"X-API-Key": self.api_key} if self.api_key else {}

    def _get(self, path: str, params=None):
        response = requests.get(
            f"{self.base_url}{path}",
            params=params,
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, payload=None):
        response = requests.post(
            f"{self.base_url}{path}",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def health(self):
        return self._get("/health")

    def readiness(self):
        return self._get("/ready")

    def portfolio_summary(self):
        return self._get("/portfolio/summary")

    def policy_summary(self, policy_id: str):
        return self._get(f"/policy/{policy_id}")

    def chat_ai(self, message: str, session_id: str = None):
        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id
        return self._post("/chat/ai", payload)

    def renewal(self, policy_id: str):
        return self._get(f"/predict/renewal/{policy_id}")

    def fraud(self, payload: dict):
        return self._post("/predict/fraud", payload)

    def underwriting(self, payload: dict):
        return self._post("/predict/underwriting", payload)

    def pending_reviews(self, limit: int = 100):
        return self._get("/human-review/pending", params={"limit": limit})

    def resolve_review(self, review_id: int, payload: dict):
        return self._post(f"/human-review/{review_id}/resolve", payload)

    def session(self, session_id: str):
        return self._get(f"/ai/session/{session_id}")

    def audit(self, session_id: str):
        return self._get(f"/ai/audit/{session_id}")

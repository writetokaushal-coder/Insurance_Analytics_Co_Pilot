import requests

DEFAULT_API_URL = "http://127.0.0.1:8001"

class InsuranceAPIClient:
    def __init__(self, base_url: str = DEFAULT_API_URL, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path, params=None):
        r = requests.get(f"{self.base_url}{path}", params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _post(self, path, payload=None):
        r = requests.post(f"{self.base_url}{path}", json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def health(self):
        return self._get("/health")

    def portfolio_summary(self):
        return self._get("/portfolio/summary")

    def policy_summary(self, policy_id):
        return self._get(f"/policy/{policy_id}")

    def chat_ai(self, message, session_id=None):
        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id
        return self._post("/chat/ai", payload)

    def renewal(self, policy_id):
        return self._get(f"/predict/renewal/{policy_id}")

    def fraud(self, payload):
        return self._post("/predict/fraud", payload)

    def underwriting(self, payload):
        return self._post("/predict/underwriting", payload)

    def pending_reviews(self, limit=100):
        return self._get("/human-review/pending", params={"limit": limit})

    def resolve_review(self, review_id, payload):
        return self._post(f"/human-review/{review_id}/resolve", payload)

    def session(self, session_id):
        return self._get(f"/ai/session/{session_id}")

    def audit(self, session_id):
        return self._get(f"/ai/audit/{session_id}")

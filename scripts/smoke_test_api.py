import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8001").rstrip("/")
api_key = os.getenv("APP_API_KEY", "").strip()
headers = {"X-API-Key": api_key} if api_key else {}

checks = [
    ("health", "/health", False),
    ("ready", "/ready", False),
    ("portfolio", "/portfolio/summary", True),
]

failed = False
for name, path, protected in checks:
    try:
        response = requests.get(
            base_url + path,
            headers=headers if protected else {},
            timeout=30,
        )
        print(name, response.status_code, response.text[:500])
        if response.status_code != 200:
            failed = True
    except Exception as error:
        print(name, "ERROR", error)
        failed = True

if failed:
    sys.exit(1)

print("API smoke test passed.")

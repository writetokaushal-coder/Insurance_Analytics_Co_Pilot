$ErrorActionPreference = "Stop"
python -m uvicorn api.production:app --host 0.0.0.0 --port 8001 --workers 1

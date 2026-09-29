STAGE 20 — FINAL HARDENING & VALIDATION
=======================================

PURPOSE

Do not add more features until the existing system passes
repeatable validation.

This stage checks:

- core Python imports
- all required ML artifacts
- FastAPI routes
- deterministic guardrails
- SQL connectivity
- Policy 360
- Ollama
- environment safety


EXECUTION

1. Extract the ZIP at project root.

2. Install:

pip install -r requirements_stage20.txt

3. Run tests:

python -m pytest tests -v

4. Run final checker:

python -m scripts.final_project_check


TARGET

All pytest tests PASS.

Final checker ends with:

FINAL RESULT: CORE PROJECT CHECK PASSED


AFTER PASSING

Backend:

python -m uvicorn api.main:app --host 127.0.0.1 --port 8001

GUI:

python -m streamlit run dashboard/streamlit_app.py


MANUAL CHECK

Overview
Policy 360
AI Copilot
Renewal
Fraud
Underwriting
Human Review
AI Audit


NEXT

Stage 20.5 / Final Delivery:
- explainability
- RAG citations
- authentication / authorization
- Docker
- GitHub cleanup
- final README
- architecture diagram
- interview-ready explanation

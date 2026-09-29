STAGE 19.5 — GUI POLISH + POLICY 360 + PORTFOLIO

Adds:
- Portfolio Overview KPIs
- Policy 360 lookup
- Improved AI Copilot page
- Improved Renewal + Underwriting cards
- Human Review Inbox
- AI Audit / Traceability
- Role-oriented UI selector

IMPORTANT:
Role selector is only a UI view, not authentication.

Execution:
1. Extract bundle at project root.
2. Patch api/main.py using STAGE19_5_MAIN_PATCH.txt.
3. pip install -r requirements_stage19_5.txt
4. python -c "from api.main import app; print('Stage 19.5 API loaded')"
5. Backend:
   python -m uvicorn api.main:app --host 127.0.0.1 --port 8001 --reload
6. GUI:
   python -m streamlit run dashboard/streamlit_app.py
7. Open http://localhost:8501

Test order:
Overview -> Policy 360 -> AI Copilot -> Renewal -> Underwriting -> Human Review -> AI Audit

Next:
Stage 20 — final hardening:
tests, auth, explainability, RAG citations, Docker, GitHub cleanup, deployment guide.

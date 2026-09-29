STAGE 18.5 — PRODUCTION INTELLIGENCE LAYER

Adds:
- SQL-persistent conversation sessions/messages
- SQL tool audit logs
- admin endpoints to inspect sessions and tool calls

Execution:
1. Run sql/04_ai_copilot_state.sql in SSMS.
2. Extract this bundle into project root.
3. Patch api/main.py using STAGE18_5_MAIN_PATCH.txt.
4. Run:
   python -m scripts.test_stage18_5
5. Test FastAPI import:
   python -c "from api.main import app; print('FastAPI + Stage 18.5 loaded successfully')"
6. Start:
   python -m uvicorn api.main:app --host 127.0.0.1 --port 8001 --reload
7. Open:
   http://127.0.0.1:8001/docs

Next:
Stage 19 — Interactive GUI.

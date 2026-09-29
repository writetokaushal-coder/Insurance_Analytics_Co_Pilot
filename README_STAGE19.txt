STAGE 19 — INTERACTIVE GUI
==========================

ARCHITECTURE

Streamlit GUI
    -> FastAPI
    -> Ollama / SQL / ML models
    -> Guardrails
    -> Human Review


FILES

dashboard/streamlit_app.py
    Main frontend.

dashboard/api_client.py
    All HTTP calls to FastAPI.

scripts/run_app.ps1
    Starts FastAPI and Streamlit.

requirements_stage19.txt
    GUI packages.


GUI PAGES

1. AI Copilot
   Natural-language conversation through /chat/ai.

2. Renewal Risk
   Calls /predict/renewal/{policy_id}.

3. Fraud Screening
   Structured fraud-risk form.

4. Underwriting
   Structured underwriting form.

5. Human Review
   Shows pending HITL queue and allows
   APPROVED / MODIFIED / REJECTED decisions.

6. AI Audit
   Shows persistent SQL conversation
   and tool-call audit.


INSTALL

Extract the ZIP at project root.

With .venv active:

pip install -r requirements_stage19.txt


MANUAL RUN

Terminal 1:

python -m uvicorn api.main:app --host 127.0.0.1 --port 8001 --reload


Terminal 2:

streamlit run dashboard/streamlit_app.py


OR

PowerShell from project root:

.\scriptsun_app.ps1


STREAMLIT

Usually opens automatically at:

http://localhost:8501


FIRST CHECK

In GUI sidebar click:

Check Backend

It should say:

API connected


THEN TEST

1. AI Copilot:
   "What can you help me with?"

2. Renewal:
   use a real POLICY_ID.

3. Underwriting:
   submit a test applicant.

4. Fraud:
   use valid category values matching training data.

5. Human Review:
   cases requiring review should appear.

6. AI Audit:
   paste/copy the AI session ID.


IMPORTANT

The GUI does not directly load ML models.

Correct architecture:

GUI
  -> API
  -> services
  -> models / SQL
  -> guardrails

This prevents business logic being duplicated
inside the UI.


NEXT

After Stage 19 works:

Stage 19.5
- improve visual design
- Policy 360 page
- charts / KPIs
- role-based views
- RAG source citations
- SHAP explanation cards
- session sidebar/history

Then final:
- testing
- Docker
- GitHub cleanup
- deployment documentation

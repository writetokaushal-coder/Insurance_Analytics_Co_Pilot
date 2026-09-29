STAGE 18 — FREE OLLAMA REPLACEMENT
==================================

WHY OLLAMA
----------
- Runs locally on your computer
- No OpenAI API key
- No API billing / credits
- Exposes a local HTTP API
- Works with LangChain
- Keeps your existing Insurance tools, ML models,
  SQL layer, guardrails and human-review system


STEP 1 — INSTALL OLLAMA
-----------------------
Install Ollama for Windows.

After installation, open a NEW PowerShell terminal.

Check:

ollama --version


STEP 2 — DOWNLOAD MODEL
-----------------------
Recommended starting model:

ollama pull qwen3:4b


STEP 3 — QUICK MODEL TEST
-------------------------
Run:

ollama run qwen3:4b

Then type:

Hello

To exit:

/bye


STEP 4 — LOCAL API
------------------
Default Ollama API:

http://127.0.0.1:11434

Check installed models:

ollama list

If Ollama is not running:

ollama serve


STEP 5 — COPY THIS BUNDLE
-------------------------
Replace:

src/llm/config.py
src/llm/copilot.py

The rest of Stage-18 stays unchanged.


STEP 6 — CHANGE .env
--------------------
Use:

LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:4b
OLLAMA_BASE_URL=http://127.0.0.1:11434

OpenAI credentials are no longer needed for this workflow.


STEP 7 — INSTALL PYTHON PACKAGE
-------------------------------
With .venv active:

pip install -r requirements_stage18_ollama.txt


STEP 8 — TEST OLLAMA FROM PYTHON
--------------------------------
Run:

python -m scripts.test_ollama_stage18

Expected:

Provider: ollama
Model: qwen3:4b
Base URL: http://127.0.0.1:11434
Response: Ollama working


STEP 9 — FASTAPI IMPORT TEST
----------------------------
Run:

python -c "from api.main import app; print('FastAPI + Ollama loaded successfully')"


STEP 10 — START FASTAPI
-----------------------
Run:

python -m uvicorn api.main:app --host 127.0.0.1 --port 8001 --reload


STEP 11 — OPEN SWAGGER
----------------------
Open:

http://127.0.0.1:8001/docs

Use the SAME endpoint:

POST /chat/ai


FIRST TEST
----------
{
  "message": "What can you help me with?"
}


RENEWAL TOOL TEST
-----------------
Use a real policy ID:

{
  "message": "Check renewal risk for POL123 and explain it."
}


UNDERWRITING TEST
-----------------
{
  "message": "Assess an applicant who is 45 years old, health score 76, BMI 28.2, credit score 720, lifestyle Good, no medical history, non-smoker, occupation risk Low."
}


IMPORTANT
---------
The LLM is local, but your important controls remain:

Ollama LLM
  -> Insurance tool
  -> Existing ML model
  -> deterministic decision_policy.py
  -> human review queue when required
  -> natural response

The local LLM is NOT allowed to override the policy engine.


SECURITY
--------
Since the previous OpenAI key was visible in a screenshot,
revoke that key from the OpenAI API Keys page.

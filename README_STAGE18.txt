STAGE 18 — LLM REASONER + TOOL CALLING
======================================

GOAL
----
Turn the existing deterministic insurance workflows into a natural
conversational AI Copilot.

IMPORTANT ARCHITECTURE
----------------------
The LLM does NOT replace your ML models or guardrails.

User
  -> LLM understands request
  -> LLM chooses a registered tool
  -> Existing Renewal/Fraud/Underwriting agent executes
  -> Existing deterministic policy engine executes
  -> Human-review queue is created when required
  -> Tool result goes back to LLM
  -> LLM explains the result naturally

Therefore the LLM cannot bypass the underlying decision policy.

TOOLS INCLUDED
--------------
1. renewal_assessment
2. fraud_screening
3. underwriting_assessment
4. policy_summary
5. portfolio_summary
6. search_insurance_knowledge


NEW FILES
---------
src/llm/config.py
    Loads OPENAI_API_KEY and OPENAI_MODEL.

src/llm/prompts.py
    System behavior and insurance safety rules.

src/llm/tools.py
    Tool definitions that wrap your existing application services.

src/llm/copilot.py
    Tool-calling reasoning loop + conversation history.

src/repositories/policy_repository.py
    Trusted read-only Policy-360 SQL queries.

src/llm/knowledge.py
    Lightweight local RAG retrieval over rag/knowledge/*.txt and *.md.

api/chat_llm.py
    POST /chat/ai endpoint.

rag/knowledge/
    Local approved knowledge documents.

scripts/test_stage18_imports.py
    Import/tool/config smoke test.


STEP 1 — EXTRACT
----------------
Extract the ZIP at the project root.


STEP 2 — INSTALL
----------------
With .venv active:

pip install -r requirements_stage18.txt


STEP 3 — CONFIGURE .env
-----------------------
Add to your existing .env:

OPENAI_API_KEY=...
OPENAI_MODEL=...

Use a model name that your OpenAI API account can access.

DO NOT commit the API key.


STEP 4 — PATCH api/main.py
--------------------------
Follow STAGE18_MAIN_PATCH.txt.


STEP 5 — IMPORT TEST
--------------------
python -m scripts.test_stage18_imports

Expected:
- Stage 18 imports loaded
- list of 6 tools
- model configuration found


STEP 6 — FASTAPI IMPORT TEST
----------------------------
python -c "from api.main import app; print('FastAPI + Stage 18 loaded successfully')"


STEP 7 — START SERVER
---------------------
python -m uvicorn api.main:app --host 127.0.0.1 --port 8001 --reload


STEP 8 — OPEN SWAGGER
---------------------
http://127.0.0.1:8001/docs

New endpoint:

POST /chat/ai


FIRST TEST
----------
{
  "message": "What can you help me with?"
}

Expected:
Natural response describing renewal, fraud, underwriting,
policy context and insurance knowledge support.


RENEWAL TEST
------------
Use a REAL policy ID:

{
  "message": "Please check renewal risk for POL123 and explain what I should do."
}

Expected flow:

LLM
 -> renewal_assessment tool
 -> renewal ML model
 -> deterministic renewal decision policy
 -> human-review queue when required
 -> LLM natural explanation


POLICY + RENEWAL COMBINED TEST
------------------------------
{
  "message": "Give me a summary of POL123 and tell me whether it is at renewal risk."
}

The LLM may call:
- policy_summary
- renewal_assessment

and combine the facts.


PORTFOLIO TEST
--------------
{
  "message": "Give me a quick overview of our insurance portfolio."
}

Expected:
portfolio_summary SQL tool.


UNDERWRITING NATURAL LANGUAGE TEST
----------------------------------
{
  "message": "Assess this applicant: age 45, health score 76, BMI 28.2, credit score 720, lifestyle Good, no medical history, non-smoker, occupation risk Low."
}

The LLM should translate the natural sentence into the
underwriting_assessment tool arguments.

If the output is Approved with Loading or Declined,
the existing decision policy may require human review.


FRAUD TEST
----------
Fraud requires many fields.

You can provide them naturally in one message or gradually across
conversation turns. The LLM should ask for missing information rather
than inventing values.

A fraud result must be explained as an investigation signal,
NOT proof of fraud.


KNOWLEDGE / RAG TEST
--------------------
Add a file:

rag/knowledge/claims_process.md

with a few paragraphs about your internal claims process.

Then ask:

{
  "message": "What is our claims escalation process?"
}

The LLM can call:
search_insurance_knowledge


SESSION MEMORY
--------------
The /chat/ai response returns session_id.

Use the same session_id on the next request:

{
  "session_id": "same-id",
  "message": "Explain that in simpler language."
}

The recent conversation is reused.


CURRENT RAG DESIGN
------------------
Stage 18 uses lightweight TF-IDF retrieval.

Why?
- no extra vector database required
- easy to debug
- works with local .txt/.md documents

Later production upgrade:
- embeddings
- vector store
- document metadata
- permission-aware retrieval
- citations


IMPORTANT HUMAN-IN-THE-LOOP RULE
--------------------------------
The LLM is only the reasoning/conversation layer.

Restricted insurance decisions remain controlled by:

src/policies/decision_policy.py

and:

analytics.human_review_queue

The LLM must not override those systems.


NEXT STAGE
----------
Stage 18.5:
- persistent memory in SQL
- better RAG with document ingestion
- model/tool observability
- audit logs
- approval context

Then Stage 19:
Interactive GUI:
- Chat panel
- Policy 360 card
- Renewal risk
- Fraud panel
- Underwriting panel
- Human review inbox
- AI explanations
- Dashboard integration

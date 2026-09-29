# Insurance AI Copilot — Final Deployment Guide

## What this final pack fixes

This pack consolidates the project before deployment:

- restores the complete Fraud GUI
- keeps Policy 360 and portfolio KPIs
- moves AI conversation memory to SQL
- logs every LLM tool call to SQL
- adds persistent RAG indexing
- asks the LLM to cite knowledge source filenames
- adds `/ready` and `/version`
- adds request IDs and request timing logs
- adds optional production API-key protection
- adds CORS configuration
- validates all eight policy types
- adds a final pre-deployment checker
- adds Windows production-like run scripts
- adds Docker templates

The trained ML models and deterministic HITL policy remain the decision core. The LLM cannot override them.

## 1. Create a checkpoint first

Before copying this pack:

```powershell
git status
git add .
git commit -m "checkpoint before final deployment pack"
```

If you do not want to commit yet, copy the project folder as a backup.

## 2. Merge this pack into the project root

Extract into:

`F:\insurance_ai_copilot`

Important files intentionally replaced by this pack:

- `src/database.py`
- `src/llm/copilot.py`
- `src/llm/prompts.py`
- `src/llm/knowledge.py`
- `dashboard/api_client.py`
- `dashboard/streamlit_app.py`

The pack does **not** replace trained predictors, services, decision policy, model artifacts, curated datasets, or your existing `api/main.py`.

## 3. Run SQL state setup

In SSMS run:

`sql/04_ai_copilot_state.sql`

Your earlier `analytics.human_review_queue` must also already exist.

## 4. Build RAG index

Put approved `.md` or `.txt` files in:

`rag/knowledge/`

Then:

```powershell
python -m scripts.build_knowledge_index
```

## 5. Local Windows `.env`

Use your existing SQL values plus:

```ini
APP_ENV=development
APP_VERSION=1.0.0
LOG_LEVEL=INFO

SQL_SERVER=YOUR_WINDOWS_SQL_SERVER
SQL_DATABASE=InsuranceAnalyticsDB
SQL_DRIVER=ODBC Driver 18 for SQL Server

LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:4b
OLLAMA_BASE_URL=http://127.0.0.1:11434

API_BASE_URL=http://127.0.0.1:8001
```

Do not set `APP_API_KEY` for ordinary local development.

## 6. Run the pre-deployment checker

```powershell
python -m scripts.predeploy_check
```

Target:

`DEPLOYMENT STATUS: READY FOR SMOKE TEST`

## 7. Run automated tests

```powershell
python -m pytest tests -v
```

Then start the API and run:

```powershell
python -m scripts.test_all_policy_types
```

## 8. Production-like local run

API terminal:

```powershell
.\scripts\run_prod_api.ps1
```

GUI terminal:

```powershell
.\scripts\run_prod_gui.ps1
```

Open:

- API docs: `http://127.0.0.1:8001/docs`
- readiness: `http://127.0.0.1:8001/ready`
- GUI: `http://127.0.0.1:8501`

## 9. Manual smoke-test checklist

Verify all of these before deployment:

1. Overview loads portfolio KPIs.
2. Policy 360 works for each of the eight product types.
3. Renewal prediction works with a real renewal-policy ID.
4. High renewal risk enters HITL when required.
5. Fraud form returns a model result.
6. Fraud alert is described as an investigation signal, not proof of fraud.
7. Fraud-risk case enters human review when required.
8. Underwriting standard approval works.
9. Underwriting Loading goes to human review.
10. Underwriting Declined goes to human review.
11. Human reviewer can APPROVE, MODIFY, or REJECT a queued item.
12. AI Copilot can answer a general question.
13. AI Copilot can call Policy Summary.
14. AI Copilot can call Renewal.
15. AI Copilot can use RAG and mention a source filename.
16. AI Audit shows tool calls.
17. Restart Uvicorn and reuse the same AI session ID.
18. Conversation history still exists after restart.
19. Stop Ollama: `/ready` should fail / return 503.
20. Restart Ollama: `/ready` becomes healthy again.

## 10. Production security

For real deployment:

```ini
APP_ENV=production
APP_API_KEY=<long-random-secret>
ALLOWED_ORIGINS=https://your-gui-domain.example
```

Give the same `APP_API_KEY` to the GUI environment. The API then requires `X-API-Key` on business routes.

## 11. Important Docker limitation

Your current Windows SQL setup appears to rely on Windows authentication.

A Linux Docker container generally cannot reuse that local Windows Trusted Connection.

For Docker deployment:

- enable SQL Server TCP/IP
- expose the SQL port you choose
- create a SQL-authenticated login
- set `SQL_USERNAME` and `SQL_PASSWORD`
- set `SQL_SERVER=host.docker.internal,1433` if SQL uses 1433

Do not start Docker deployment until the normal Windows production-like run passes.

## 12. Ollama and Docker

If Ollama remains on Windows host:

```ini
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Ollama must be reachable from the container.

## 13. Freeze exact dependencies

Model artifacts can be sensitive to XGBoost / scikit-learn versions.

With the working `.venv` active:

```powershell
.\scripts\export_requirements_lock.ps1
```

This creates `requirements.lock.txt` for Docker.

## 14. Docker test

Copy:

`.env.docker.example` -> `.env.docker`

Fill real values, then:

```powershell
docker compose -f deployment/docker-compose.yml build
docker compose -f deployment/docker-compose.yml up
```

## 15. Claims you should avoid in README/interviews

- annual premium represented by the portfolio is not automatically accounting revenue
- fraud score is not proof of fraud
- underwriting model is decision support, not uncontrolled final authority
- source `POLICY_STATUS` is not a reconstructed actuarial in-force status
- formal loss ratio requires aligned earned premium and incurred claims
- known source-date inconsistencies were flagged rather than silently deleted

## Recommended deployment order

1. merge final pack
2. run SQL AI-state script
3. build RAG index
4. run predeploy checker
5. run pytest
6. run all-policy-type test
7. run local production-like smoke test
8. create Git checkpoint/tag
9. freeze dependencies
10. test Docker
11. move to remote deployment

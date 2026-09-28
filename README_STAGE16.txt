STAGE 16 GAP COMPLETION
=======================

WHAT THIS BUNDLE ADDS
---------------------
1. src/models/underwriting_predictor.py
2. src/services/underwriting_service.py
3. src/policies/decision_policy.py
4. src/repositories/renewal_repository.py
5. src/repositories/human_review_repository.py
6. src/services/human_review_service.py
7. api/schemas.py
8. api/main.py
9. sql/03_human_review_queue.sql
10. scripts/sync_ml_feature_tables.py
11. project_audit.py

IMPORTANT
---------
Your existing:
- src/services/renewal_service.py
- src/services/fraud_service.py
- src/models/fraud_predictor.py
- src/renewal_predictor.py

are intentionally NOT included here so that this bundle does not overwrite
your existing working versions.

COPY ORDER
----------
1. Copy the files/folders into the project root.
2. Make sure these model artifacts exist:
   models/renewal_xgboost_model.joblib
   models/renewal_churn_threshold.joblib
   models/fraud_xgboost_model.joblib
   models/fraud_threshold.joblib
   models/underwriting_xgboost_model.joblib
   models/underwriting_label_encoder.joblib

3. Run:
   python project_audit.py

4. Run SQL Server script:
   sql/03_human_review_queue.sql

5. Sync curated ML feature datasets to SQL:
   python scripts/sync_ml_feature_tables.py

6. Start API:
   python -m uvicorn api.main:app --host 127.0.0.1 --port 8001 --reload

7. Open:
   http://127.0.0.1:8001/docs

EXPECTED ENDPOINTS
------------------
GET  /
GET  /health
GET  /predict/renewal/{policy_id}
POST /predict/fraud
POST /predict/underwriting
GET  /human-review/pending
POST /human-review/{review_id}/resolve

NEXT
----
After the API smoke test is clean, continue with:
Stage 17 - Agentic Insurance AI Orchestrator
Then:
RAG -> conversation state -> approval workflow -> interactive GUI.

STAGE 20.1 — ALL POLICY TYPE VALIDATION

This stage explicitly checks all expected policy types:

Health
Motor
Term Life
Commercial
Home
Personal Accident
Whole Life
Travel

Before running:
1. FastAPI must be running on port 8001.
2. Ideally these SQL tables exist:
   analytics.renewal_model_features
   analytics.fraud_model_features
   analytics.underwriting_model_features

Run database policy coverage:
python -m pytest tests/test_policy_type_coverage.py -v

Run end-to-end policy-type validation:
python -m scripts.test_all_policy_types

Report:
reports/policy_type_test_results.csv

Result meanings:
PASS = endpoint/model worked.
NO_DATA = no matching model-feature record existed.
SKIP_MISSING_FIELDS = matching row existed but API-required fields were null/missing.
FAIL_HTTP_xxx = API failure that must be fixed.
ERROR = connection/runtime failure.

Important:
Policy 360 should PASS for every policy type.
For Renewal/Fraud/Underwriting, NO_DATA may be a dataset-coverage limitation rather than an application bug.

Also manually test:
- invalid policy ID
- missing fields
- bad categorical input
- high renewal-risk human review
- fraud alert human review
- underwriting Loading human review
- underwriting Declined human review
- human APPROVED/MODIFIED/REJECTED actions
- API restart + session persistence
- Ollama unavailable
- SQL unavailable
- all GUI pages
- AI audit trail

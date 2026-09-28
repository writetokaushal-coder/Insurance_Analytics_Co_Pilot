import pandas as pd
import requests
from pathlib import Path
from sqlalchemy import text
from src.database import engine

API_BASE_URL = "http://127.0.0.1:8001"

EXPECTED_POLICY_TYPES = [
    "Health",
    "Motor",
    "Term Life",
    "Commercial",
    "Home",
    "Personal Accident",
    "Whole Life",
    "Travel",
]

FRAUD_FIELDS = [
    "CLAIM_ID","CLAIM_AMOUNT","REPORTING_DELAY_DAYS","INCIDENT_MONTH",
    "AGE","ANNUAL_INCOME","CREDIT_SCORE","SUM_INSURED","ANNUAL_PREMIUM",
    "RISK_SCORE","CLAIM_TYPE","SOURCE","CLAIM_SEVERITY","GENDER",
    "MARITAL_STATUS","OCCUPATION","STATE","CUSTOMER_RISK_SEGMENT",
    "POLICY_TYPE","PAYMENT_MODE","RISK_BAND",
]

UNDERWRITING_FIELDS = [
    "AGE","HEALTH_SCORE","BMI","CREDIT_SCORE",
    "LIFESTYLE","MEDICAL_HISTORY_FLAG","SMOKER_FLAG","OCCUPATION_RISK",
]

PROJECT_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def table_exists(name):
    q = text("SELECT CASE WHEN OBJECT_ID(:name,'U') IS NOT NULL THEN 1 ELSE 0 END")
    with engine.connect() as c:
        return bool(c.execute(q, {"name": name}).scalar())

def get_counts():
    q = text("""
        SELECT POLICY_TYPE, COUNT(*) AS POLICY_COUNT
        FROM analytics.policy_360
        GROUP BY POLICY_TYPE
        ORDER BY POLICY_TYPE
    """)
    with engine.connect() as c:
        return pd.DataFrame(c.execute(q).mappings().all())

def sample_policy(policy_type):
    q = text("""
        SELECT TOP 1 POLICY_ID
        FROM analytics.policy_360
        WHERE POLICY_TYPE=:policy_type
        ORDER BY POLICY_ID
    """)
    with engine.connect() as c:
        return c.execute(q, {"policy_type": policy_type}).scalar()

def sample_renewal_policy(policy_type):
    if not table_exists("analytics.renewal_model_features"):
        return None
    q = text("""
        SELECT TOP 1 r.POLICY_ID
        FROM analytics.renewal_model_features r
        JOIN analytics.policy_360 p ON p.POLICY_ID=r.POLICY_ID
        WHERE p.POLICY_TYPE=:policy_type
        ORDER BY r.POLICY_ID
    """)
    with engine.connect() as c:
        return c.execute(q, {"policy_type": policy_type}).scalar()

def sample_model_row(table_name, policy_type):
    if not table_exists(f"analytics.{table_name}"):
        return None
    q = text(f"""
        SELECT TOP 1 f.*
        FROM analytics.{table_name} f
        JOIN analytics.policy_360 p ON p.POLICY_ID=f.POLICY_ID
        WHERE p.POLICY_TYPE=:policy_type
    """)
    with engine.connect() as c:
        row = c.execute(q, {"policy_type": policy_type}).mappings().first()
    return dict(row) if row else None

def api_get(path):
    try:
        r = requests.get(API_BASE_URL + path, timeout=120)
        return r.status_code, r.json()
    except Exception as e:
        return None, {"error": str(e)}

def api_post(path, payload):
    try:
        r = requests.post(API_BASE_URL + path, json=payload, timeout=120)
        return r.status_code, r.json()
    except Exception as e:
        return None, {"error": str(e)}

def clean_payload(row, fields):
    result = {}
    for field in fields:
        value = row.get(field)
        if pd.isna(value):
            value = None
        if hasattr(value, "item"):
            try:
                value = value.item()
            except Exception:
                pass
        result[field] = value
    return result

def label(code):
    if code == 200:
        return "PASS"
    if code is None:
        return "ERROR"
    return f"FAIL_HTTP_{code}"

def main():
    health_code, _ = api_get("/health")
    if health_code != 200:
        raise RuntimeError("Start FastAPI on http://127.0.0.1:8001 before running this script.")

    counts = get_counts()
    print("\nPOLICY TYPE COUNTS")
    print(counts.to_string(index=False))

    actual_types = set(counts["POLICY_TYPE"].dropna())
    missing_types = set(EXPECTED_POLICY_TYPES) - actual_types
    if missing_types:
        print("\nWARNING - missing expected types:", sorted(missing_types))

    results = []

    for policy_type in EXPECTED_POLICY_TYPES:
        print("\n" + "-" * 70)
        print("Testing:", policy_type)

        rec = {
            "POLICY_TYPE": policy_type,
            "POLICY_360": "NO_DATA",
            "RENEWAL": "NO_DATA",
            "FRAUD": "NO_DATA",
            "UNDERWRITING": "NO_DATA",
        }

        pid = sample_policy(policy_type)
        if pid:
            code, _ = api_get(f"/policy/{pid}")
            rec["SAMPLE_POLICY_ID"] = pid
            rec["POLICY_360"] = label(code)
            print("Policy 360:", rec["POLICY_360"], pid)

        rpid = sample_renewal_policy(policy_type)
        if rpid:
            code, _ = api_get(f"/predict/renewal/{rpid}")
            rec["RENEWAL_POLICY_ID"] = rpid
            rec["RENEWAL"] = label(code)
            print("Renewal:", rec["RENEWAL"], rpid)
        else:
            print("Renewal: NO_DATA")

        frow = sample_model_row("fraud_model_features", policy_type)
        if frow:
            payload = clean_payload(frow, FRAUD_FIELDS)
            missing = [k for k, v in payload.items() if v is None]
            if missing:
                rec["FRAUD"] = "SKIP_MISSING_FIELDS"
                rec["FRAUD_NOTE"] = ",".join(missing)
                print("Fraud: SKIP_MISSING_FIELDS", missing)
            else:
                code, _ = api_post("/predict/fraud", payload)
                rec["FRAUD"] = label(code)
                rec["FRAUD_CLAIM_ID"] = payload.get("CLAIM_ID")
                print("Fraud:", rec["FRAUD"], payload.get("CLAIM_ID"))
        else:
            print("Fraud: NO_DATA")

        urow = sample_model_row("underwriting_model_features", policy_type)
        if urow:
            payload = clean_payload(urow, UNDERWRITING_FIELDS)
            missing = [k for k, v in payload.items() if v is None]
            if missing:
                rec["UNDERWRITING"] = "SKIP_MISSING_FIELDS"
                rec["UNDERWRITING_NOTE"] = ",".join(missing)
                print("Underwriting: SKIP_MISSING_FIELDS", missing)
            else:
                code, _ = api_post("/predict/underwriting", payload)
                rec["UNDERWRITING"] = label(code)
                print("Underwriting:", rec["UNDERWRITING"])
        else:
            print("Underwriting: NO_DATA")

        results.append(rec)

    df = pd.DataFrame(results)
    path = REPORT_DIR / "policy_type_test_results.csv"
    df.to_csv(path, index=False)

    print("\n" + "=" * 70)
    print(df.to_string(index=False))
    print("\nSaved:", path)
    print("\nInterpretation:")
    print("PASS = worked end-to-end")
    print("NO_DATA = model feature table had no matching row")
    print("SKIP_MISSING_FIELDS = test row lacked required API fields")
    print("FAIL_HTTP_xxx / ERROR = fix required")

if __name__ == "__main__":
    main()

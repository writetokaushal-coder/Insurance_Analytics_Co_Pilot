from sqlalchemy import text
from src.database import engine

EXPECTED_POLICY_TYPES = {
    "Health",
    "Motor",
    "Term Life",
    "Commercial",
    "Home",
    "Personal Accident",
    "Whole Life",
    "Travel",
}

def test_all_expected_policy_types_exist():
    q = text("""
        SELECT DISTINCT POLICY_TYPE
        FROM analytics.policy_360
        WHERE POLICY_TYPE IS NOT NULL
    """)
    with engine.connect() as c:
        actual = {row[0] for row in c.execute(q)}
    missing = EXPECTED_POLICY_TYPES - actual
    assert not missing, f"Missing policy types: {sorted(missing)}"

def test_each_policy_type_has_rows():
    q = text("""
        SELECT POLICY_TYPE, COUNT(*) AS CNT
        FROM analytics.policy_360
        GROUP BY POLICY_TYPE
    """)
    with engine.connect() as c:
        counts = {row[0]: row[1] for row in c.execute(q)}
    for policy_type in EXPECTED_POLICY_TYPES:
        assert counts.get(policy_type, 0) > 0, f"No rows for {policy_type}"

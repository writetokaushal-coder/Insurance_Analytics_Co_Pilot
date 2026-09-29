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

    # One DISTINCT query is enough:
    # if a policy type appears here,
    # it automatically has at least one row.
    query = text(
        """
        SELECT DISTINCT
            POLICY_TYPE
        FROM analytics.policy_360
        WHERE POLICY_TYPE IS NOT NULL
        """
    )

    with engine.connect() as connection:

        actual_policy_types = {
            row[0]
            for row
            in connection.execute(query)
        }

    missing_policy_types = (
        EXPECTED_POLICY_TYPES
        -
        actual_policy_types
    )

    assert not missing_policy_types, (
        "Missing policy types: "
        f"{sorted(missing_policy_types)}"
    )from sqlalchemy import text

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

    # One DISTINCT query is enough:
    # if a policy type appears here,
    # it automatically has at least one row.
    query = text(
        """
        SELECT DISTINCT
            POLICY_TYPE
        FROM analytics.policy_360
        WHERE POLICY_TYPE IS NOT NULL
        """
    )

    with engine.connect() as connection:

        actual_policy_types = {
            row[0]
            for row
            in connection.execute(query)
        }

    missing_policy_types = (
        EXPECTED_POLICY_TYPES
        -
        actual_policy_types
    )

    assert not missing_policy_types, (
        "Missing policy types: "
        f"{sorted(missing_policy_types)}"
    )
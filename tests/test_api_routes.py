EXPECTED_ROUTES = {
    "/",
    "/health",
    "/predict/renewal/{policy_id}",
    "/predict/fraud",
    "/predict/underwriting",
    "/human-review/pending",
    "/human-review/{review_id}/resolve",
    "/chat/ai",
    "/portfolio/summary",
    "/policy/{policy_id}",
}


def test_expected_routes_are_registered():
    from api.main import app

    paths = set(
        app.openapi()["paths"].keys()
    )

    missing = EXPECTED_ROUTES - paths

    assert not missing, (
        f"Missing API routes: {sorted(missing)}"
    )

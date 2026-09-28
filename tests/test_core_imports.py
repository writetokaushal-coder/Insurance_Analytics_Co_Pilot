def test_api_import():
    from api.main import app
    assert app is not None


def test_database_import():
    from src.database import engine
    assert engine is not None


def test_renewal_predictor_import():
    from src.renewal_predictor import predict_renewal
    assert callable(predict_renewal)


def test_fraud_predictor_import():
    from src.models.fraud_predictor import predict_fraud
    assert callable(predict_fraud)


def test_underwriting_predictor_import():
    from src.models.underwriting_predictor import predict_underwriting
    assert callable(predict_underwriting)


def test_services_import():
    from src.services.renewal_service import assess_renewal
    from src.services.fraud_service import assess_fraud
    from src.services.underwriting_service import assess_underwriting

    assert callable(assess_renewal)
    assert callable(assess_fraud)
    assert callable(assess_underwriting)


def test_llm_import():
    from src.llm.copilot import run_insurance_copilot
    assert callable(run_insurance_copilot)

from app.reasoning.severity_classifier import SeverityClassifier


def test_critical_for_payment_issue():
    assert SeverityClassifier().classify("Users are charged twice", "payment-service") == "Critical"


def test_high_for_login_failure():
    assert SeverityClassifier().classify("Many users cannot log in after deployment", "auth-service") == "High"


def test_medium_for_latency():
    assert SeverityClassifier().classify("Some users report slow latency", "api-service") == "Medium"


def test_low_for_minor_issue():
    assert SeverityClassifier().classify("Small warning with no impact", "worker") == "Low"


def test_critical_matches_security_keyword():
    assert SeverityClassifier().classify("Security breach suspected in SSO", "auth-service") == "Critical"


def test_medium_matches_partial_keyword():
    assert SeverityClassifier().classify("Queues are partially blocked", "worker") == "Medium"


def test_returns_low_when_no_heuristic_matches():
    assert SeverityClassifier().classify("Interesting observation", None) == "Low"

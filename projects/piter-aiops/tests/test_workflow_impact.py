"""Severity-based demo business impact estimates."""
from __future__ import annotations

from app.workflow_impact import SEVERITY_IMPACT, severity_impact


def test_severity_impact_table():
    assert severity_impact("P1") == (30, 5000)
    assert severity_impact("P2") == (15, 2500)
    assert severity_impact("P3") == (5, 500)


def test_severity_impact_defaults_to_p3():
    assert severity_impact(None) == SEVERITY_IMPACT["P3"]
    assert severity_impact("unknown") == SEVERITY_IMPACT["P3"]

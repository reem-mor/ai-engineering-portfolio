"""Validate static JSON datasets and corpus filename alignment."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.data_loader import grouped_example_questions, load_example_questions, load_workflow_alerts

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "sample_documents"
EVAL_PATH = ROOT / "evaluation" / "test_questions.json"


def test_example_questions_unique_labels_and_text():
    items = load_example_questions()
    assert len(items) >= 3
    questions = [i["question"] for i in items]
    assert len(questions) == len(set(questions))
    for item in items:
        assert item.get("label")
        assert len(item["question"]) >= 10


def test_grouped_examples_cover_all_questions():
    flat = [i["question"] for i in load_example_questions()]
    grouped = grouped_example_questions()
    assert sum(len(v) for v in grouped.values()) == len(flat)


def test_workflow_alerts_have_required_fields():
    alerts = load_workflow_alerts()
    assert alerts
    ids = [a["id"] for a in alerts]
    assert len(ids) == len(set(ids))
    for alert in alerts:
        for key in ("id", "severity", "service", "title", "question"):
            assert key in alert


def test_evaluation_questions_schema():
    cases = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    assert isinstance(cases, list)
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids))
    corpus_names = {p.stem for p in CORPUS.iterdir() if p.is_file()}
    corpus_names |= {p.name for p in CORPUS.iterdir() if p.is_file()}
    for case in cases:
        if case.get("expect_validation_error"):
            assert case.get("expected_reason")
            continue
        if case.get("expect_grounded"):
            for fragment in case.get("expected_source_contains", []):
                assert any(fragment in name for name in corpus_names), (
                    f"eval id {case['id']}: no corpus file matching {fragment!r}"
                )

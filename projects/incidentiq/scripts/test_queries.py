"""Phase 9 end-to-end validation runner — exercises the live RAG pipeline against 10 canned cases.

Runs 7 standard queries (must retrieve and answer), 2 edge cases that must
raise validation errors (empty / oversized question), and 1 irrelevant query
(must return confidence='none' or zero sources). Prints a per-test summary
followed by an aggregate PASSED/FAILED verdict and exits non-zero on any
failure so it slots into CI.
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

_PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from pydantic import ValidationError  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.core.rag_pipeline import RAGPipeline, init_pipeline  # noqa: E402
from app.core.retriever import init_retriever  # noqa: E402
from app.models.schemas import QueryRequest, RAGResponse  # noqa: E402
from app.utils.logger import get_logger  # noqa: E402

_logger = get_logger(__name__)

_THICK_RULE: str = "=" * 58
_THIN_RULE: str = "\u2501" * 58
_VALID_CONFIDENCE: frozenset[str] = frozenset({"high", "medium", "low", "none"})


@dataclass(slots=True)
class TestCase:
    """A single validation case: a question plus its acceptance criteria."""

    number: int
    question: str
    allowed_confidence: frozenset[str]
    min_retrieved: int
    expect_validation_error: bool = False
    irrelevant: bool = False


def _build_cases() -> list[TestCase]:
    """Return the ordered list of 10 Phase 9 validation cases."""
    standard = frozenset({"high", "medium"})
    standard_relaxed = frozenset({"high", "medium", "low"})

    return [
        TestCase(
            number=1,
            question="What are the triage steps for a P1 Kubernetes pod crash loop?",
            allowed_confidence=standard,
            min_retrieved=1,
        ),
        TestCase(
            number=2,
            question="How do I resolve PostgreSQL connection pool exhaustion?",
            allowed_confidence=standard,
            min_retrieved=1,
        ),
        TestCase(
            number=3,
            question="What is the SOP for Kafka consumer lag incidents?",
            allowed_confidence=standard,
            min_retrieved=1,
        ),
        TestCase(
            number=4,
            question="We are seeing 5xx errors spiking on our API gateway, what do I do?",
            allowed_confidence=standard_relaxed,
            min_retrieved=1,
        ),
        TestCase(
            number=5,
            question="What was the root cause of the last MongoDB replication failure?",
            allowed_confidence=standard_relaxed,
            min_retrieved=1,
        ),
        TestCase(
            number=6,
            question="How do I handle an AWS IAM permission denied error during deployment?",
            allowed_confidence=standard_relaxed,
            min_retrieved=1,
        ),
        TestCase(
            number=7,
            question="What do I do if the load balancer health checks are failing?",
            allowed_confidence=standard_relaxed,
            min_retrieved=1,
        ),
        TestCase(
            number=8,
            question="",
            allowed_confidence=frozenset(),
            min_retrieved=0,
            expect_validation_error=True,
        ),
        TestCase(
            number=9,
            question="What is the weather in Paris today?",
            allowed_confidence=frozenset(_VALID_CONFIDENCE),
            min_retrieved=0,
            irrelevant=True,
        ),
        TestCase(
            number=10,
            question="x" * 600,
            allowed_confidence=frozenset(),
            min_retrieved=0,
            expect_validation_error=True,
        ),
    ]


def _print_header(case: TestCase) -> None:
    """Print the per-test header banner."""
    preview = case.question if case.question else "<empty string>"
    if len(preview) > 60:
        preview = preview[:60]
    print(_THIN_RULE)
    print(f"Test {case.number}: {preview}...")
    print(_THIN_RULE)


def _print_result(
    *,
    confidence: str,
    sources: int,
    elapsed_ms: int,
    answer: str,
    passed: bool,
    reason: str | None,
) -> None:
    """Print the per-test result block in the exact format required."""
    answer_preview = answer.replace("\n", " ")[:300]
    verdict = "\u2713 PASS" if passed else "\u2717 FAIL"
    print(f"Confidence  : {confidence}")
    print(f"Sources     : {sources}")
    print(f"Time        : {elapsed_ms}ms")
    print(f"Answer      : {answer_preview}...")
    print(f"Result      : {verdict}")
    if not passed and reason:
        print(f"Reason      : {reason}")
    print()


async def _run_standard_case(
    case: TestCase, pipeline: RAGPipeline
) -> tuple[bool, str | None]:
    """Run a standard (or irrelevant) case end-to-end and emit its result block."""
    try:
        request = QueryRequest(question=case.question)
    except (ValidationError, ValueError) as exc:
        _print_result(
            confidence="-",
            sources=0,
            elapsed_ms=0,
            answer="(no answer — request rejected at validation)",
            passed=False,
            reason=f"Unexpected validation error: {exc}",
        )
        return False, f"Unexpected validation error: {exc}"

    try:
        response: RAGResponse = await pipeline.query(request)
    except Exception as exc:  # noqa: BLE001
        _print_result(
            confidence="-",
            sources=0,
            elapsed_ms=0,
            answer="(no answer — pipeline raised)",
            passed=False,
            reason=f"Pipeline raised {type(exc).__name__}: {exc}",
        )
        return False, f"Pipeline raised {type(exc).__name__}: {exc}"

    passed: bool = True
    reason: str | None = None

    if case.irrelevant:
        if response.confidence != "none" and response.retrieved_count != 0:
            passed = False
            reason = (
                "Irrelevant query returned relevant results: "
                f"confidence={response.confidence} retrieved={response.retrieved_count}"
            )
    else:
        if response.confidence not in case.allowed_confidence:
            passed = False
            reason = (
                f"confidence={response.confidence!r} not in {sorted(case.allowed_confidence)}"
            )
        elif response.retrieved_count < case.min_retrieved:
            passed = False
            reason = (
                f"retrieved_count={response.retrieved_count} < required {case.min_retrieved}"
            )

    _print_result(
        confidence=response.confidence,
        sources=response.retrieved_count,
        elapsed_ms=response.processing_time_ms,
        answer=response.answer,
        passed=passed,
        reason=reason,
    )
    return passed, reason


def _run_validation_error_case(case: TestCase) -> tuple[bool, str | None]:
    """Run a case that MUST raise a Pydantic/value validation error at request construction."""
    raised: bool = False
    exc_type: str = "-"
    try:
        QueryRequest(question=case.question)
    except (ValidationError, ValueError) as exc:
        raised = True
        exc_type = type(exc).__name__
        _ = exc
    except Exception as exc:  # noqa: BLE001
        _print_result(
            confidence="-",
            sources=0,
            elapsed_ms=0,
            answer=f"(unexpected exception type: {type(exc).__name__})",
            passed=False,
            reason=f"Expected ValidationError/ValueError, got {type(exc).__name__}: {exc}",
        )
        return False, f"Expected ValidationError/ValueError, got {type(exc).__name__}"

    if raised:
        _print_result(
            confidence="n/a",
            sources=0,
            elapsed_ms=0,
            answer=f"(rejected at validation as expected: {exc_type})",
            passed=True,
            reason=None,
        )
        return True, None

    _print_result(
        confidence="-",
        sources=0,
        elapsed_ms=0,
        answer="(no exception raised)",
        passed=False,
        reason="Expected ValidationError/ValueError but none was raised",
    )
    return False, "Expected ValidationError/ValueError but none was raised"


async def main() -> int:
    """Execute all 10 Phase 9 cases sequentially and return a process exit code."""
    settings = get_settings()
    init_retriever(settings.faiss_index_path)
    pipeline: RAGPipeline = init_pipeline()

    cases: list[TestCase] = _build_cases()
    passed_count: int = 0
    failed_count: int = 0

    for case in cases:
        _print_header(case)
        if case.expect_validation_error:
            ok, _ = _run_validation_error_case(case)
        else:
            ok, _ = await _run_standard_case(case, pipeline)
        if ok:
            passed_count += 1
        else:
            failed_count += 1

    print(_THICK_RULE)
    print("PHASE 9 TEST SUMMARY")
    print(_THICK_RULE)
    print(f"Total  : {len(cases)}")
    print(f"Passed : {passed_count}")
    print(f"Failed : {failed_count}")
    print(_THICK_RULE)
    overall: str = "PASSED" if failed_count == 0 else "FAILED"
    print(f"Overall: {overall}")
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

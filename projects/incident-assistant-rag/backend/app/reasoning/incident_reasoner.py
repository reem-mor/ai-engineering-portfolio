from __future__ import annotations

import json
import re
from typing import Any

from app.rag.generator import OpenAIAnswerGenerator
from app.rag.prompt_builder import PromptBuilder
from app.rag.rag_pipeline import RAGPipeline
from app.rag.retriever import Retriever
from app.schemas.incident_schema import IncidentAnalysisResponse


class IncidentReasoner:
    """
    Incident-specific reasoning layer.

    Supports two modes:

    1. Production mode:
       IncidentReasoner.create_default()
       -> uses RAGPipeline.create_default()

    2. Test-compatible mode:
       IncidentReasoner(fake_retriever, answer_generator=fake_generator)
       -> uses retriever + prompt builder + answer generator directly
    """

    def __init__(
        self,
        rag_pipeline_or_retriever: RAGPipeline | Retriever | Any | None = None,
        answer_generator: Any | None = None,
        score_threshold: float = 0.25,
    ) -> None:
        if isinstance(rag_pipeline_or_retriever, RAGPipeline):
            self.rag_pipeline: RAGPipeline | None = rag_pipeline_or_retriever
            self.retriever = None
        else:
            self.rag_pipeline = None
            self.retriever = rag_pipeline_or_retriever or Retriever()

        self.prompt_builder = PromptBuilder()
        self.answer_generator = answer_generator or OpenAIAnswerGenerator()
        self.score_threshold = score_threshold

    @classmethod
    def create_default(cls) -> "IncidentReasoner":
        return cls(rag_pipeline_or_retriever=RAGPipeline.create_default())

    def analyze(
        self,
        description: str,
        affected_service: str | None = None,
        environment: str | None = None,
        top_k: int = 5,
    ) -> IncidentAnalysisResponse:
        description = self._clean_required_text(description, "Incident description")
        affected_service = self._clean_optional_text(affected_service)
        environment = self._clean_optional_text(environment)

        if top_k < 1:
            raise ValueError("top_k must be positive.")

        question = self._build_incident_question(
            description=description,
            affected_service=affected_service,
            environment=environment,
        )

        if self.rag_pipeline is not None:
            rag_response = self.rag_pipeline.answer_question(
                question=question,
                top_k=top_k,
            )

            answer = getattr(rag_response, "answer", "") or ""
            sources = getattr(rag_response, "sources", []) or []
            retrieved_chunks = getattr(rag_response, "retrieved_chunks", []) or []
            confidence = getattr(rag_response, "confidence", "medium") or "medium"
            used_context = bool(getattr(rag_response, "used_context", False))

        else:
            retrieved_chunks = self.retriever.retrieve(question=question, top_k=top_k)
            relevant_chunks = [
                chunk for chunk in retrieved_chunks if chunk.score >= self.score_threshold
            ]

            prompt = self.prompt_builder.build(
                question=question,
                retrieved_chunks=relevant_chunks,
            )

            answer = self.answer_generator.generate(prompt)

            sources = sorted({chunk.source_file for chunk in relevant_chunks})
            retrieved_chunks = relevant_chunks
            confidence = self._calculate_confidence(relevant_chunks)
            used_context = bool(relevant_chunks)

        parsed = self._try_parse_json_answer(answer)

        severity = parsed.get("severity") or self._detect_severity(
            description=description,
            answer=answer,
            environment=environment,
        )

        likely_causes = parsed.get("likely_causes") or self._extract_likely_causes(
            description=description,
            answer=answer,
        )

        recommended_checks = parsed.get("recommended_checks") or self._extract_recommended_checks(
            answer=answer,
        )

        missing_information = parsed.get("missing_information") or self._build_missing_information(
            affected_service=affected_service,
            environment=environment,
        )

        next_best_action = parsed.get("next_best_action") or self._build_next_best_action(
            severity=severity,
            answer=answer,
        )

        escalation_recommendation = parsed.get(
            "escalation_recommendation"
        ) or self._build_escalation_recommendation(
            severity=severity,
            answer=answer,
            affected_service=affected_service,
        )

        return IncidentAnalysisResponse(
            incident_summary=parsed.get("incident_summary") or description,
            severity=severity,
            likely_causes=self._ensure_list(likely_causes),
            recommended_checks=self._ensure_list(recommended_checks),
            missing_information=self._ensure_list(missing_information),
            next_best_action=next_best_action,
            escalation_recommendation=escalation_recommendation,
            sources=sources,
            retrieved_chunks=retrieved_chunks,
            confidence=confidence,
            used_context=used_context,
        )

    @staticmethod
    def _try_parse_json_answer(answer: str) -> dict[str, Any]:
        """
        Best-effort JSON parser for tests/fake generators.

        Production does not depend on this, but tests may use fake generators
        that return JSON-like incident analysis.
        """
        if not answer.strip():
            return {}

        try:
            parsed = json.loads(answer)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", answer, re.DOTALL)

        if not match:
            return {}

        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _clean_required_text(value: str | None, field_name: str) -> str:
        if value is None:
            raise ValueError(f"{field_name} is required.")

        cleaned = " ".join(value.strip().split())

        if not cleaned:
            raise ValueError(f"{field_name} is required.")

        return cleaned

    @staticmethod
    def _clean_optional_text(value: str | None) -> str | None:
        if value is None:
            return None

        cleaned = " ".join(value.strip().split())
        return cleaned or None

    @staticmethod
    def _build_incident_question(
        description: str,
        affected_service: str | None,
        environment: str | None,
    ) -> str:
        service = affected_service or "unknown service"
        env = environment or "unknown environment"

        return (
            "Analyze this operational incident using only the indexed incident "
            "knowledge base. Include severity, likely causes, recommended checks, "
            "missing information, next best action, and escalation guidance.\n\n"
            f"Incident description: {description}\n"
            f"Affected service: {service}\n"
            f"Environment: {env}"
        )

    @staticmethod
    def _detect_severity(
        description: str,
        answer: str,
        environment: str | None,
    ) -> str:
        description_text = f"{description} {environment or ''}".lower()
        answer_text = answer.lower()

        critical_description_signals = [
            "all users",
            "everyone",
            "entire platform",
            "production down",
            "complete outage",
            "system down",
            "service down",
            "data loss",
            "security incident",
            "breach",
            "payment risk",
            "duplicate charge",
            "duplicate charges",
            "financial impact",
        ]

        if any(signal in description_text for signal in critical_description_signals):
            return "Critical"

        high_description_signals = [
            "many users",
            "multiple users",
            "cannot log in",
            "can't log in",
            "login failure",
            "production login",
            "major 5xx",
            "unavailable service",
        ]

        if any(signal in description_text for signal in high_description_signals):
            return "High"

        high_answer_signals = [
            "high severity",
            "classify the incident as high",
            "backend team",
            "service owner",
            "production login failure",
        ]

        if any(signal in answer_text for signal in high_answer_signals):
            return "High"

        medium_signals = [
            "medium",
            "partial degradation",
            "latency",
            "slow",
            "timeout",
            "staging",
        ]

        if any(signal in description_text or signal in answer_text for signal in medium_signals):
            return "Medium"

        low_signals = [
            "low",
            "warning",
            "no user impact",
        ]

        if any(signal in description_text or signal in answer_text for signal in low_signals):
            return "Low"

        if environment and environment.lower() == "production":
            return "High"

        return "Medium"

    @staticmethod
    def _extract_likely_causes(description: str, answer: str) -> list[str]:
        text = f"{description} {answer}".lower()
        causes: list[str] = []

        if "deployment" in text or "release" in text:
            causes.append(
                "Recent deployment introduced a regression, configuration change, or incompatible release."
            )

        if "jwt" in text or "token" in text:
            causes.append("JWT/token validation or authentication configuration issue.")

        if "environment variable" in text or "env" in text:
            causes.append("Incorrect or changed environment variables after deployment.")

        if "database" in text or "connection" in text:
            causes.append("Database connectivity or dependency failure affecting authentication.")

        if "auth" in text or "login" in text:
            causes.append("Auth-service failure or degraded authentication dependency.")

        if not causes:
            causes.append(
                "The knowledge base does not contain enough information to infer a specific root cause."
            )

        return causes

    @staticmethod
    def _extract_recommended_checks(answer: str) -> list[str]:
        text = answer.lower()
        checks: list[str] = []

        rules = [
            (
                ["auth logs", "auth-service logs", "logs"],
                "Check auth-service logs for authentication errors.",
            ),
            (
                ["health endpoint", "health check"],
                "Check the affected service health endpoint.",
            ),
            (
                ["deployment logs", "deployment", "release"],
                "Check deployment status, deployment logs, and the currently running version.",
            ),
            (
                ["jwt", "token"],
                "Validate JWT secrets, token configuration, and auth-related environment variables.",
            ),
            (
                ["environment variables", "env"],
                "Compare current environment variables with the previous working release.",
            ),
            (
                ["database", "connection"],
                "Check database connectivity from the affected service.",
            ),
            (
                ["error rate", "latency", "dashboard", "monitoring"],
                "Check monitoring dashboards for error rate, latency, and affected scope.",
            ),
            (
                ["rollback"],
                "Prepare rollback if the deployment is confirmed as the cause.",
            ),
        ]

        for keywords, recommendation in rules:
            if any(keyword in text for keyword in keywords):
                if recommendation not in checks:
                    checks.append(recommendation)

        if not checks:
            checks = [
                "Check the affected service health endpoint.",
                "Check application logs for recent errors.",
                "Check recent deployments and configuration changes.",
                "Check monitoring dashboards for error rate and latency.",
            ]

        return checks

    @staticmethod
    def _build_missing_information(
        affected_service: str | None,
        environment: str | None,
    ) -> list[str]:
        missing: list[str] = []

        if not affected_service:
            missing.append("Affected service name is missing.")

        if not environment:
            missing.append("Environment is missing.")

        missing.extend(
            [
                "Exact incident start time.",
                "Number or percentage of affected users.",
                "Relevant HTTP status codes and error messages.",
                "Latest deployment version, commit SHA, or release ID.",
                "Whether rollback was already attempted.",
            ]
        )

        return missing

    @staticmethod
    def _build_next_best_action(severity: str, answer: str) -> str:
        text = answer.lower()

        if "deployment" in text or "release" in text:
            return (
                "Check deployment logs, service health, auth logs, and environment "
                "variables immediately. If the issue started after the release, prepare rollback."
            )

        if severity in {"Critical", "High"}:
            return (
                "Start incident triage immediately, confirm user impact, check logs "
                "and dashboards, and involve the relevant service owner."
            )

        return "Collect more evidence from logs, dashboards, and recent changes before escalating."

    @staticmethod
    def _build_escalation_recommendation(
        severity: str,
        answer: str,
        affected_service: str | None,
    ) -> str:
        text = answer.lower()

        if "backend team" in text:
            return "Escalate to the backend team."

        if "payments team" in text:
            return "Escalate to the payments team."

        if "dba" in text:
            return "Escalate to the DBA team."

        if severity == "Critical":
            return "Escalate immediately to the incident commander and service owner."

        if severity == "High":
            if affected_service:
                return f"Escalate to the {affected_service} owner and backend team."
            return "Escalate to the relevant service owner and backend team."

        return "Monitor the issue and escalate if user impact increases."

    @staticmethod
    def _calculate_confidence(chunks: list[Any]) -> str:
        if not chunks:
            return "none"

        best_score = max(chunk.score for chunk in chunks)

        if best_score >= 0.75:
            return "high"

        if best_score >= 0.5:
            return "medium"

        return "low"

    @staticmethod
    def _ensure_list(value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, list):
            return [str(item) for item in value]

        return [str(value)]
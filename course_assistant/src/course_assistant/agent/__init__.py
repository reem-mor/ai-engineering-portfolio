"""LangGraph agent (Phase 5).

Wires the tools into a stateful graph with a bilingual (HE/EN) system prompt and
guardrails (never fabricate course facts; cite sources; stay on course topics).
The LLM is mocked in tests — no paid calls in CI.
"""

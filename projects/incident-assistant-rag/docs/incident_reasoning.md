# Incident Reasoning

Incident reasoning is separate from normal chat because incident response requires structured output, not only a free text answer.

## Output Fields

The incident analysis endpoint returns:

- incident summary
- severity
- likely causes
- recommended checks
- missing information
- next best action
- escalation recommendation
- sources
- confidence
- retrieved chunks

## Severity Classification

Severity is calculated deterministically with keyword rules. This keeps severity stable and explainable.

## LLM Usage

The LLM is asked to return structured JSON using only retrieved context. If the LLM returns invalid JSON, the backend uses a safe fallback response.

## No Hidden Reasoning

The app does not expose hidden chain-of-thought. It provides a practical reasoning summary that is safe and useful for operations.

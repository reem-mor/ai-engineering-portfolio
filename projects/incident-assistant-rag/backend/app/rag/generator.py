from abc import ABC, abstractmethod

from openai import OpenAI

from app.core.config import settings


class BaseAnswerGenerator(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class OpenAIAnswerGenerator(BaseAnswerGenerator):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.answer_model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for answer generation.")
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a careful incident assistant. Answer only from provided context."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""


class FakeAnswerGenerator(BaseAnswerGenerator):
    def generate(self, prompt: str) -> str:
        if "did not return relevant context" in prompt.lower():
            return "The knowledge base does not contain enough information to answer this question."
        return "Based on the retrieved incident context, check service health, logs, recent deployments, and escalate if users are affected."


class FakeIncidentAnswerGenerator(BaseAnswerGenerator):
    def generate(self, prompt: str) -> str:
        return """
{
  "incident_summary": "Users cannot log in after deployment.",
  "severity": "High",
  "likely_causes": ["Recent deployment changed authentication behavior", "Authentication service configuration issue"],
  "recommended_checks": ["Check auth-service health endpoint", "Check auth-service logs", "Check recent deployments", "Check authentication environment variables"],
  "missing_information": ["Exact error message", "Number of affected users", "Deployment timestamp"],
  "next_best_action": "Check auth-service logs and health before restarting the service.",
  "escalation_recommendation": "Escalate to the backend team if many users are affected or production login is failing."
}
""".strip()

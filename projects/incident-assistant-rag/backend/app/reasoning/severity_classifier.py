class SeverityClassifier:
    CRITICAL_KEYWORDS = {"payment", "payments", "charged", "duplicate payment", "data loss", "security", "production down", "database outage", "critical", "all users"}
    HIGH_KEYWORDS = {"login failed", "cannot log in", "many users", "production", "timeout", "500", "major", "unavailable"}
    MEDIUM_KEYWORDS = {"slow", "latency", "degraded", "partial", "some users", "staging"}

    def classify(self, description: str, affected_service: str | None = None) -> str:
        text = f"{description} {affected_service or ''}".lower()
        if self._contains_any(text, self.CRITICAL_KEYWORDS):
            return "Critical"
        if self._contains_any(text, self.HIGH_KEYWORDS):
            return "High"
        if self._contains_any(text, self.MEDIUM_KEYWORDS):
            return "Medium"
        return "Low"

    def _contains_any(self, text: str, keywords: set[str]) -> bool:
        return any(keyword in text for keyword in keywords)

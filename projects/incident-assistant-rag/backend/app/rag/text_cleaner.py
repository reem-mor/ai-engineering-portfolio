import re


class TextCleaner:
    def clean(self, text: str) -> str:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = "\n".join(line.strip() for line in cleaned.splitlines())
        cleaned = cleaned.strip()

        if not cleaned:
            raise ValueError("Cleaned text cannot be empty.")

        return cleaned

from openai import OpenAI

from .base_ai import BaseAI
from ..config import Config


class OpenRouterAI(BaseAI):
    """Optional alternate provider, kept for comparison/fallback."""

    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.OPENROUTER_API_KEY,
        )
        self.model = Config.OPENROUTER_MODEL

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

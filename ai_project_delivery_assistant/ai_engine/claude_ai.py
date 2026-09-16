from anthropic import Anthropic

from .base_ai import BaseAI
from ..config import Config


class ClaudeAI(BaseAI):
    """Real Claude (Anthropic) provider - this is the whole point of Phase 1."""

    def __init__(self):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL

    def generate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        # Claude can return multiple content blocks; join any text ones.
        return "".join(
            block.text for block in response.content if block.type == "text"
        )

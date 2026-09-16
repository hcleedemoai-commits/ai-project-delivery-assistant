from .base_ai import BaseAI


class MockAI(BaseAI):
    """
    Fake provider for offline testing - no API key or internet needed.
    Set AI_PROVIDER=mock in .env to use this instead of a real call.
    """

    def generate(self, prompt: str) -> str:
        return (
            '{"missing_information": ["Acceptance Criteria"], '
            '"risks": ["Business scope requires clarification"], '
            '"questions": ["Who is the business owner?"]}'
        )

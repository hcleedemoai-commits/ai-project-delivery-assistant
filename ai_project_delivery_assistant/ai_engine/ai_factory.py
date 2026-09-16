from ..config import Config
from .claude_ai import ClaudeAI
from .mock_ai import MockAI


class AIFactory:
    """
    Single switch point for which AI provider the app uses.
    Controlled entirely by AI_PROVIDER in .env - never hardcode a provider
    elsewhere in the app.
    """

    @staticmethod
    def create():
        provider = Config.AI_PROVIDER

        if provider == "claude":
            return ClaudeAI()

        elif provider == "mock":
            return MockAI()

        elif provider == "openrouter":
            # imported lazily so the app doesn't need the openai package
            # installed unless this branch is actually used
            from .openrouter_ai import OpenRouterAI
            return OpenRouterAI()

        raise ValueError(f"Unknown AI provider: {provider!r}")

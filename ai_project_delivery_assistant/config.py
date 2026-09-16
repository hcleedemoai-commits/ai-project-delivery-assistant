import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    """Configuration management for the AI Project Delivery Assistant."""

    # Which AI provider to use: claude | openrouter | mock
    AI_PROVIDER = os.getenv("AI_PROVIDER", "claude")

    # Claude (Anthropic)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    # OpenRouter (optional alternate provider)
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct")

    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    SAMPLE_DATA_DIR = os.path.join(BASE_DIR, "sample_data")

    @classmethod
    def validate(cls):
        """Raise a clear error if the selected provider isn't configured yet."""

        if cls.AI_PROVIDER == "claude":
            if not cls.ANTHROPIC_API_KEY or cls.ANTHROPIC_API_KEY == "your-api-key-here":
                raise ValueError(
                    "ANTHROPIC_API_KEY not set. Add it to .env, or get one at "
                    "https://console.anthropic.com/"
                )

        elif cls.AI_PROVIDER == "openrouter":
            if not cls.OPENROUTER_API_KEY or cls.OPENROUTER_API_KEY == "your-api-key-here":
                raise ValueError(
                    "OPENROUTER_API_KEY not set. Add it to .env, or get one at "
                    "https://openrouter.ai/"
                )

        elif cls.AI_PROVIDER == "mock":
            pass  # no key needed

        else:
            raise ValueError(f"Unknown AI_PROVIDER: {cls.AI_PROVIDER!r}")

        return True

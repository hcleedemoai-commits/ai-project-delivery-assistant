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

    # Notion (Phase 5 integration)
    NOTION_API_KEY = os.getenv("NOTION_API_KEY")
    NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")

    # Jira (Phase 5 integration - Meeting Action Items)
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
    JIRA_ISSUE_TYPE = os.getenv("JIRA_ISSUE_TYPE", "Task")

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

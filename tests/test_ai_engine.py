"""
Smoke tests that don't need a real API key - they only exercise the
mock provider and the response parser. Run with: pytest
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["AI_PROVIDER"] = "mock"

from ai_project_delivery_assistant.ai_engine.ai_factory import AIFactory
from ai_project_delivery_assistant.ai_engine.mock_ai import MockAI
from ai_project_delivery_assistant.ai_engine.response_parser import AIResponseParser


def test_factory_returns_mock_provider():
    ai = AIFactory.create()
    assert isinstance(ai, MockAI)


def test_mock_provider_returns_parseable_json():
    ai = MockAI()
    result = ai.generate("any prompt")
    parsed = AIResponseParser().parse(result)

    assert "missing_information" in parsed
    assert "risks" in parsed
    assert "questions" in parsed


def test_parser_extracts_json_from_noisy_text():
    noisy = 'Sure, here you go:\n{"risks": ["Timeline delay"], "questions": []}\nHope that helps!'
    parsed = AIResponseParser().parse(noisy)

    assert parsed["risks"] == ["Timeline delay"]


def test_parser_falls_back_gracefully_on_non_json():
    parsed = AIResponseParser().parse("This is not JSON at all.")
    assert "error" in parsed

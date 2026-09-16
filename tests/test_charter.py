"""
Offline tests for the Phase 2 Charter feature - no API key needed.
Run with: pytest
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_project_delivery_assistant.prompts.charter_prompt import build_charter_prompt
from ai_project_delivery_assistant.generators.charter_generator import CharterGenerator


SAMPLE_CHARTER_DATA = {
    "project_name": "Customer Portal",
    "business_objective": "Let customers self-serve order history and invoices.",
    "in_scope": ["Login", "Order history view", "Invoice download"],
    "out_of_scope": ["Payment processing"],
    "constraints": ["Must launch within 3 months"],
    "assumptions": ["Customers already have accounts"],
    "stakeholders": ["Head of Support", "IT Manager"],
}


def test_prompt_includes_the_idea_text():
    prompt = build_charter_prompt("Build a customer self-service portal.")
    assert "Build a customer self-service portal." in prompt
    assert "JSON" in prompt


def test_charter_generator_produces_a_docx(tmp_path):
    output_file = tmp_path / "charter.docx"

    CharterGenerator().generate(SAMPLE_CHARTER_DATA, str(output_file))

    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_charter_generator_handles_missing_fields_gracefully(tmp_path):
    output_file = tmp_path / "charter_minimal.docx"

    # Only project_name provided - every other field should default to empty
    CharterGenerator().generate({"project_name": "Minimal Project"}, str(output_file))

    assert output_file.exists()

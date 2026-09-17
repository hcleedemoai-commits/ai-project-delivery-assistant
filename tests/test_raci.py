"""
Offline tests for the Phase 4 RACI Matrix feature - no API key needed.
Run with: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_project_delivery_assistant.prompts.raci_prompt import build_raci_prompt
from ai_project_delivery_assistant.generators.raci_generator import RaciGenerator
from ai_project_delivery_assistant.raci_rules import validate_raci


ROLES = ["Project Manager", "Business Analyst", "Technical Lead"]
ACTIVITIES = ["Gather requirements", "Build login flow", "Sign off scope"]

VALID_ASSIGNMENTS = {
    "Gather requirements": {"Project Manager": "A", "Business Analyst": "R", "Technical Lead": "C"},
    "Build login flow": {"Project Manager": "I", "Business Analyst": "R", "Technical Lead": "A"},
    "Sign off scope": {"Project Manager": "A", "Business Analyst": "R", "Technical Lead": ""},
}

# missing an "A" on the first activity, and two "A"s on the second
INVALID_ASSIGNMENTS = {
    "Gather requirements": {"Project Manager": "R", "Business Analyst": "R", "Technical Lead": ""},
    "Build login flow": {"Project Manager": "A", "Business Analyst": "A", "Technical Lead": "R"},
    "Sign off scope": {"Project Manager": "A", "Business Analyst": "R", "Technical Lead": ""},
}

SAMPLE_RACI_DATA = {
    "activities": ACTIVITIES,
    "roles": ROLES,
    "assignments": VALID_ASSIGNMENTS,
}


def test_raci_prompt_includes_idea_and_the_accountable_rule():
    prompt = build_raci_prompt("Build a customer portal.")
    assert "Build a customer portal." in prompt
    assert "exactly one role as Accountable" in prompt


def test_validate_raci_passes_a_correctly_formed_matrix():
    warnings = validate_raci(ACTIVITIES, ROLES, VALID_ASSIGNMENTS)
    assert warnings == []


def test_validate_raci_flags_missing_accountable():
    warnings = validate_raci(ACTIVITIES, ROLES, INVALID_ASSIGNMENTS)
    assert any("Gather requirements" in w and "no Accountable" in w for w in warnings)


def test_validate_raci_flags_duplicate_accountable():
    warnings = validate_raci(ACTIVITIES, ROLES, INVALID_ASSIGNMENTS)
    assert any("Build login flow" in w and "2 Accountable" in w for w in warnings)


def test_validate_raci_handles_missing_activity_entry_without_crashing():
    warnings = validate_raci(["Untracked activity"], ROLES, {})
    assert any("Untracked activity" in w for w in warnings)


def test_raci_generator_produces_a_docx_with_matrix_and_clean_validation(tmp_path):
    output_file = tmp_path / "raci_matrix.docx"

    RaciGenerator().generate(SAMPLE_RACI_DATA, str(output_file))

    assert output_file.exists()

    from docx import Document
    doc = Document(str(output_file))

    table_text = "\n".join(
        cell.text for table in doc.tables for row in table.rows for cell in row.cells
    )
    paragraph_text = "\n".join(p.text for p in doc.paragraphs)

    assert "Gather requirements" in table_text
    assert "No issues found" in paragraph_text


def test_raci_generator_surfaces_validation_warnings_in_the_document(tmp_path):
    output_file = tmp_path / "raci_matrix_invalid.docx"
    data = {"activities": ACTIVITIES, "roles": ROLES, "assignments": INVALID_ASSIGNMENTS}

    RaciGenerator().generate(data, str(output_file))

    from docx import Document
    doc = Document(str(output_file))
    paragraph_text = "\n".join(p.text for p in doc.paragraphs)

    assert "no Accountable" in paragraph_text


def test_raci_generator_handles_missing_data_gracefully(tmp_path):
    output_file = tmp_path / "raci_matrix_empty.docx"

    RaciGenerator().generate({}, str(output_file))

    assert output_file.exists()

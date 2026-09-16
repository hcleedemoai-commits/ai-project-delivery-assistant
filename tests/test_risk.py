"""
Offline tests for the Phase 3 Risk Register feature - no API key needed.
Run with: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_project_delivery_assistant.prompts.risk_prompt import build_risk_prompt
from ai_project_delivery_assistant.generators.risk_generator import RiskGenerator
from ai_project_delivery_assistant.escalation import needs_escalation


SAMPLE_RISK_DATA = {
    "risks": [
        {
            "risk_description": "Legacy invoicing system has no public API",
            "likelihood": "High",
            "impact": "High",
            "mitigation": "Confirm API availability with vendor in week 1",
            "owner": "Technical Lead",
        },
        {
            "risk_description": "Stakeholders disagree on invoice date format",
            "likelihood": "Medium",
            "impact": "Low",
            "mitigation": "Confirm format in the kickoff workshop",
            "owner": "Business Analyst",
        },
    ]
}


def test_risk_prompt_includes_idea_and_asks_for_json_keys():
    prompt = build_risk_prompt("Build a customer portal.")
    assert "Build a customer portal." in prompt
    assert "risks (list of objects" in prompt
    assert '"likelihood"' in prompt


def test_risk_prompt_does_not_ask_ai_to_decide_escalation():
    # escalation is a fixed rule applied in Python, not an AI judgement call
    prompt = build_risk_prompt("Build a customer portal.")
    assert "escalat" not in prompt.lower()


def test_needs_escalation_high_impact_alone_escalates():
    assert needs_escalation("Low", "High") is True


def test_needs_escalation_high_likelihood_and_medium_impact_escalates():
    assert needs_escalation("High", "Medium") is True


def test_needs_escalation_low_likelihood_and_low_impact_does_not_escalate():
    assert needs_escalation("Low", "Low") is False


def test_needs_escalation_handles_unrecognised_values_without_crashing():
    # AI wording won't always exactly match "Low"/"Medium"/"High"
    assert needs_escalation("Unclear", "Unclear") is False


def test_risk_generator_produces_a_docx_with_table_and_escalation_summary(tmp_path):
    output_file = tmp_path / "risk_register.docx"

    RiskGenerator().generate(SAMPLE_RISK_DATA, str(output_file))

    assert output_file.exists()

    from docx import Document
    doc = Document(str(output_file))

    table_text = "\n".join(
        cell.text for table in doc.tables for row in table.rows for cell in row.cells
    )
    paragraph_text = "\n".join(p.text for p in doc.paragraphs)

    # the high/high risk shows up in the table...
    assert "Legacy invoicing system" in table_text
    # ...and, because it meets the escalation rule, in the summary section too
    assert "Legacy invoicing system" in paragraph_text
    # the low/medium risk should NOT appear in the escalation summary
    assert "Stakeholders disagree" not in paragraph_text


def test_risk_generator_handles_missing_risks_gracefully(tmp_path):
    output_file = tmp_path / "risk_register_empty.docx"

    RiskGenerator().generate({}, str(output_file))

    assert output_file.exists()

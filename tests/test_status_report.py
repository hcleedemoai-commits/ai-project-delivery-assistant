"""
Offline tests for the Phase 4 Status Report / audience-tone feature -
no API key needed. Run with: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_project_delivery_assistant.prompts.status_report_prompt import (
    AUDIENCES,
    build_status_report_prompt,
)
from ai_project_delivery_assistant.generators.status_report_generator import StatusReportGenerator


SAMPLE_STATUS_DATA = {
    "report_title": "Customer Portal - Week 6 Status",
    "summary": "The portal is broadly on track, with one schedule risk on invoicing.",
    "highlights": ["Login flow complete and in QA"],
    "risks_or_blockers": ["Invoicing API is undocumented, causing a delay"],
    "next_steps": ["Finish reverse-engineering the invoicing API"],
}


def test_audiences_contains_exactly_executive_and_team():
    assert set(AUDIENCES) == {"Executive", "Team"}


def test_executive_prompt_asks_for_business_language_not_jargon():
    prompt = build_status_report_prompt("Some status notes.", "Executive")
    assert "business impact" in prompt.lower()
    assert "avoid technical jargon" in prompt.lower()


def test_team_prompt_asks_for_technical_task_level_detail():
    prompt = build_status_report_prompt("Some status notes.", "Team")
    assert "technical detail" in prompt.lower()
    assert "concrete work items" in prompt.lower()


def test_both_audiences_receive_the_same_underlying_status_notes():
    exec_prompt = build_status_report_prompt("Login flow is done.", "Executive")
    team_prompt = build_status_report_prompt("Login flow is done.", "Team")

    # same facts...
    assert "Login flow is done." in exec_prompt
    assert "Login flow is done." in team_prompt
    # ...but genuinely different instructions, not just a label swap
    assert exec_prompt != team_prompt


def test_unknown_audience_falls_back_to_team_instructions_without_crashing():
    prompt = build_status_report_prompt("Some status notes.", "Stakeholder Committee")
    assert "technical detail" in prompt.lower()


def test_status_report_generator_produces_a_docx(tmp_path):
    output_file = tmp_path / "status_report.docx"

    StatusReportGenerator().generate(SAMPLE_STATUS_DATA, str(output_file))

    assert output_file.exists()

    from docx import Document
    doc = Document(str(output_file))
    paragraph_text = "\n".join(p.text for p in doc.paragraphs)

    assert "Week 6 Status" in paragraph_text
    assert "invoicing API" in paragraph_text


def test_status_report_generator_handles_missing_data_gracefully(tmp_path):
    output_file = tmp_path / "status_report_empty.docx"

    StatusReportGenerator().generate({}, str(output_file))

    assert output_file.exists()

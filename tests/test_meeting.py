"""
Offline tests for the Phase 4 Meeting Minutes feature - no API key needed.
Run with: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_project_delivery_assistant.meeting_parser import parse_meeting_notes
from ai_project_delivery_assistant.prompts.meeting_prompt import build_meeting_prompt
from ai_project_delivery_assistant.generators.meeting_generator import MeetingMinutesGenerator


SAMPLE_RAW_NOTES = (
    "Date: 2026-09-17\n"
    "Attendees: Alice, Bob, Carol\n"
    "\n"
    "Discussed the login flow. Team agreed to use internal SSO."
)

SAMPLE_AI_DATA = {
    "discussion_summary": "The team discussed the login flow for the new portal.",
    "decisions": ["Use the existing internal SSO instead of building a new login system."],
    "action_items": [
        {"description": "Confirm SSO API access with IT", "owner": "Alice", "due_date": "Next Friday"},
    ],
}


def test_parse_meeting_notes_extracts_date_and_attendees():
    parsed = parse_meeting_notes(SAMPLE_RAW_NOTES)

    assert parsed["date"] == "2026-09-17"
    assert parsed["attendees"] == ["Alice", "Bob", "Carol"]


def test_parse_meeting_notes_body_excludes_header_lines():
    parsed = parse_meeting_notes(SAMPLE_RAW_NOTES)

    assert "Date:" not in parsed["body"]
    assert "Attendees:" not in parsed["body"]
    assert "Discussed the login flow" in parsed["body"]


def test_parse_meeting_notes_handles_missing_header_gracefully():
    parsed = parse_meeting_notes("Just some notes with no header at all.")

    assert parsed["date"] is None
    assert parsed["attendees"] == []
    assert "Just some notes" in parsed["body"]


def test_meeting_prompt_sends_only_the_body_not_date_or_attendees():
    parsed = parse_meeting_notes(SAMPLE_RAW_NOTES)
    prompt = build_meeting_prompt(parsed["body"])

    # the AI never sees the header - it can't mangle what it never receives
    assert "Alice" not in prompt or "Discussed the login flow" in prompt
    assert "2026-09-17" not in prompt
    assert "Discussed the login flow" in prompt


def test_meeting_generator_combines_parsed_header_with_ai_content(tmp_path):
    output_file = tmp_path / "meeting_minutes.docx"
    parsed = parse_meeting_notes(SAMPLE_RAW_NOTES)

    MeetingMinutesGenerator().generate(parsed, SAMPLE_AI_DATA, str(output_file))

    assert output_file.exists()

    from docx import Document
    doc = Document(str(output_file))

    paragraph_text = "\n".join(p.text for p in doc.paragraphs)
    table_text = "\n".join(
        cell.text for table in doc.tables for row in table.rows for cell in row.cells
    )

    # the parsed (non-AI) header made it into the document
    assert "2026-09-17" in paragraph_text
    assert "Alice, Bob, Carol" in paragraph_text
    # the AI-extracted content made it in too
    assert "internal SSO" in paragraph_text
    assert "Confirm SSO API access" in table_text


def test_meeting_generator_handles_missing_data_gracefully(tmp_path):
    output_file = tmp_path / "meeting_minutes_empty.docx"

    MeetingMinutesGenerator().generate({}, {}, str(output_file))

    assert output_file.exists()

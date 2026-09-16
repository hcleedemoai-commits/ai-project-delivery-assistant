"""
Offline tests for the Phase 2 Milestones & Timeline feature - no API key needed.
Run with: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_project_delivery_assistant.prompts.timeline_prompt import build_timeline_prompt
from ai_project_delivery_assistant.generators.timeline_generator import TimelineGenerator


SAMPLE_PHASES = [
    {
        "phase_name": "Requirements & Design",
        "phase_goal": "Confirm scope and UI design.",
        "tasks": [{"id": "T1", "description": "Run stakeholder workshop", "priority": "High"}],
    },
    {
        "phase_name": "Build",
        "phase_goal": "Implement the portal.",
        "tasks": [{"id": "T2", "description": "Build login flow", "priority": "High"}],
    },
]

SAMPLE_TIMELINE_DATA = {
    "project_name": "Customer Portal",
    "milestones": [
        {
            "phase_name": "Requirements & Design",
            "milestone_name": "Scope Signed Off",
            "description": "Stakeholders approve scope and design.",
        },
        {
            "phase_name": "Build",
            "milestone_name": "Portal Feature-Complete",
            "description": "All planned features implemented.",
        },
    ],
    "sequencing_notes": [
        "Build must follow Requirements & Design - implementation needs an approved design first."
    ],
}


def test_timeline_prompt_includes_project_and_phase_data():
    prompt = build_timeline_prompt("Customer Portal", SAMPLE_PHASES)
    assert "Customer Portal" in prompt
    assert "Run stakeholder workshop" in prompt
    assert "milestones" in prompt
    assert "sequencing_notes" in prompt


def test_timeline_prompt_omits_task_ids_and_priority_to_stay_lean():
    prompt = build_timeline_prompt("Customer Portal", SAMPLE_PHASES)
    # the prompt should carry the task description, not the raw id/priority fields
    assert '"id"' not in prompt
    assert '"priority"' not in prompt


def test_timeline_generator_produces_a_docx(tmp_path):
    output_file = tmp_path / "timeline.docx"

    TimelineGenerator().generate(SAMPLE_TIMELINE_DATA, str(output_file))

    assert output_file.exists()

    from docx import Document
    doc = Document(str(output_file))

    # milestones are written into a table, not plain paragraphs -
    # check both, the same way a human opening the file actually would
    paragraph_text = "\n".join(p.text for p in doc.paragraphs)
    table_text = "\n".join(
        cell.text for table in doc.tables for row in table.rows for cell in row.cells
    )
    assert "Scope Signed Off" in table_text
    assert "Build must follow" in paragraph_text


def test_timeline_generator_handles_missing_milestones_gracefully(tmp_path):
    output_file = tmp_path / "timeline_empty.docx"

    TimelineGenerator().generate({"project_name": "Test"}, str(output_file))

    assert output_file.exists()

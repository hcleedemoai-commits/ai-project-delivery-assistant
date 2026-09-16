"""
Offline tests for the Phase 2 WBS feature - no API key needed.
Run with: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_project_delivery_assistant.prompts.wbs_prompt import (
    build_wbs_phases_prompt,
    build_wbs_tasks_prompt,
)
from ai_project_delivery_assistant.generators.wbs_generator import WBSGenerator


SAMPLE_WBS_DATA = {
    "project_name": "Customer Portal",
    "phases": [
        {
            "phase_name": "Requirements & Design",
            "phase_goal": "Confirm scope and UI design.",
            "tasks": [
                {"id": "T1", "description": "Run stakeholder workshop", "priority": "High"},
                {"id": "T2", "description": "Draft wireframes", "priority": "Medium"},
            ],
        },
        {
            "phase_name": "Build",
            "phase_goal": "Implement the portal.",
            "tasks": [
                {"id": "T3", "description": "Build login flow", "priority": "High"},
            ],
        },
    ],
}


def test_phases_prompt_includes_idea_and_asks_for_phases_only():
    prompt = build_wbs_phases_prompt("Build a customer portal.")
    assert "Build a customer portal." in prompt
    assert "phases" in prompt
    assert '"tasks"' not in prompt  # step 1 asks for the phases key only, not a tasks key


def test_tasks_prompt_includes_phase_context():
    prompt = build_wbs_tasks_prompt("Build a customer portal.", "Build", "Implement the portal.")
    assert "Build a customer portal." in prompt
    assert "Implement the portal." in prompt


def test_wbs_generator_produces_a_docx_with_all_phases(tmp_path):
    output_file = tmp_path / "wbs.docx"

    WBSGenerator().generate(SAMPLE_WBS_DATA, str(output_file))

    assert output_file.exists()

    from docx import Document
    doc = Document(str(output_file))
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "Requirements & Design" in text
    assert "Build" in text


def test_wbs_generator_handles_a_phase_with_no_tasks(tmp_path):
    output_file = tmp_path / "wbs_empty_phase.docx"
    data = {
        "project_name": "Test Project",
        "phases": [{"phase_name": "Planning", "phase_goal": "", "tasks": []}],
    }

    WBSGenerator().generate(data, str(output_file))

    assert output_file.exists()

"""
Offline tests for the Phase 3 Decision Matrix feature - no API key needed.
Run with: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_project_delivery_assistant.prompts.decision_prompt import build_decision_prompt
from ai_project_delivery_assistant.generators.decision_generator import DecisionGenerator
from ai_project_delivery_assistant.decision_matrix import compute_weighted_totals, rank_options


SAMPLE_CRITERIA = [
    {"name": "Cost", "weight": 8},
    {"name": "Speed", "weight": 4},
]

SAMPLE_SCORES = {
    "Build in-house": {
        "Cost": {"score": 2, "rationale": "High upfront engineering cost"},
        "Speed": {"score": 2, "rationale": "Slowest to ship"},
    },
    "Use third-party provider": {
        "Cost": {"score": 4, "rationale": "Subscription cost, no build cost"},
        "Speed": {"score": 5, "rationale": "Fastest to integrate"},
    },
}

SAMPLE_DECISION_DATA = {
    "decision_context": "How to build authentication for the customer portal.",
    "options": ["Build in-house", "Use third-party provider"],
    "criteria": SAMPLE_CRITERIA,
    "scores": SAMPLE_SCORES,
}


def test_decision_prompt_includes_idea_and_asks_for_json_keys():
    prompt = build_decision_prompt("Decide on an authentication approach.")
    assert "Decide on an authentication approach." in prompt
    assert "options (list of strings)" in prompt
    assert '"score"' in prompt


def test_decision_prompt_does_not_ask_ai_to_pick_a_winner():
    # the weighted total and recommendation are computed in Python, not asked of the AI
    prompt = build_decision_prompt("Decide on an authentication approach.")
    assert "weighted total" not in prompt.lower()
    assert "recommend" not in prompt.lower()


def test_compute_weighted_totals_matches_hand_calculation():
    totals = compute_weighted_totals(SAMPLE_CRITERIA, SAMPLE_SCORES)

    # Build in-house:  8*2 + 4*2 = 24
    # Third-party:      8*4 + 4*5 = 52
    assert totals["Build in-house"] == 24
    assert totals["Use third-party provider"] == 52


def test_rank_options_orders_highest_total_first():
    totals = compute_weighted_totals(SAMPLE_CRITERIA, SAMPLE_SCORES)
    ranked = rank_options(totals)

    assert ranked[0][0] == "Use third-party provider"
    assert ranked[-1][0] == "Build in-house"


def test_compute_weighted_totals_handles_missing_cells_without_crashing():
    incomplete_scores = {"Only Option": {"Cost": {"score": 3}}}  # missing "Speed" entirely
    totals = compute_weighted_totals(SAMPLE_CRITERIA, incomplete_scores)

    # missing "Speed" cell contributes 0, not a crash
    assert totals["Only Option"] == 8 * 3 + 4 * 0


def test_decision_generator_produces_a_docx_with_recommendation(tmp_path):
    output_file = tmp_path / "decision_matrix.docx"

    DecisionGenerator().generate(SAMPLE_DECISION_DATA, str(output_file))

    assert output_file.exists()

    from docx import Document
    doc = Document(str(output_file))

    table_text = "\n".join(
        cell.text for table in doc.tables for row in table.rows for cell in row.cells
    )
    paragraph_text = "\n".join(p.text for p in doc.paragraphs)

    assert "Use third-party provider" in table_text
    # the recommendation names the actual computed winner, not a placeholder
    assert "Recommended option: Use third-party provider" in paragraph_text


def test_decision_generator_handles_missing_data_gracefully(tmp_path):
    output_file = tmp_path / "decision_matrix_empty.docx"

    DecisionGenerator().generate({}, str(output_file))

    assert output_file.exists()

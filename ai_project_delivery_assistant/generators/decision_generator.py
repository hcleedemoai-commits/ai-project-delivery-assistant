from .base_generator import BaseGenerator
from ..decision_matrix import compute_weighted_totals, rank_options


class DecisionGenerator(BaseGenerator):
    """
    Builds a Decision Matrix Word document from the structured dict
    returned by AIResponseParser after calling build_decision_prompt().

    Expected shape of `data`:
        {
            "decision_context": str,
            "options": [str, ...],
            "criteria": [{"name": str, "weight": number}, ...],
            "scores": {
                option_name: {
                    criterion_name: {"score": number, "rationale": str},
                    ...
                },
                ...
            },
        }

    The weighted totals and the recommendation are computed here, from
    decision_matrix.py - not read from `data` - for the same reason
    RiskGenerator computes escalation itself instead of trusting the AI.
    """

    def build(self, data: dict):
        doc = self.document

        options = data.get("options", [])
        criteria = data.get("criteria", [])
        scores = data.get("scores", {})

        doc.add_heading("Decision Matrix", level=1)
        doc.add_paragraph(data.get("decision_context", "Untitled decision"))

        doc.add_heading("1. Criteria & Weights", level=2)
        if not criteria:
            doc.add_paragraph("No criteria generated.")
        else:
            table = doc.add_table(rows=1, cols=2)
            table.style = "Table Grid"
            header = table.rows[0].cells
            header[0].text = "Criterion"
            header[1].text = "Weight"
            for c in criteria:
                row = table.add_row().cells
                row[0].text = str(c.get("name", ""))
                row[1].text = str(c.get("weight", ""))

        doc.add_heading("2. Scoring Matrix", level=2)
        if not options or not criteria:
            doc.add_paragraph("No scoring matrix generated.")
        else:
            table = doc.add_table(rows=1, cols=len(criteria) + 1)
            table.style = "Table Grid"
            header = table.rows[0].cells
            header[0].text = "Option"
            for i, c in enumerate(criteria):
                header[i + 1].text = str(c.get("name", ""))

            for option in options:
                row = table.add_row().cells
                row[0].text = str(option)
                option_scores = scores.get(option, {})
                for i, c in enumerate(criteria):
                    cell = option_scores.get(c.get("name", ""), {})
                    score = cell.get("score", "")
                    rationale = cell.get("rationale", "")
                    row[i + 1].text = f"{score} — {rationale}" if rationale else str(score)

        doc.add_heading("3. Weighted Recommendation", level=2)
        if not options or not criteria:
            doc.add_paragraph("No recommendation - not enough data to score.")
        else:
            totals = compute_weighted_totals(criteria, scores)
            ranked = rank_options(totals)

            table = doc.add_table(rows=1, cols=2)
            table.style = "Table Grid"
            header = table.rows[0].cells
            header[0].text = "Option"
            header[1].text = "Weighted Total"
            for option_name, total in ranked:
                row = table.add_row().cells
                row[0].text = str(option_name)
                row[1].text = str(total)

            if ranked:
                winner, winning_total = ranked[0]
                doc.add_paragraph(
                    f"Recommended option: {winner} (weighted total: {winning_total}). "
                    "This total is computed directly from the criteria weights and "
                    "scores above - not asked of the AI - so re-running this report "
                    "on the same inputs always produces the same recommendation."
                )

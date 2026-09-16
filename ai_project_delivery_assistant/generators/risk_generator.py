from .base_generator import BaseGenerator
from ..escalation import needs_escalation


class RiskGenerator(BaseGenerator):
    """
    Builds a Risk Register Word document from the structured dict
    returned by AIResponseParser after calling build_risk_prompt().

    Expected shape of `data`:
        {
            "risks": [
                {
                    "risk_description": str,
                    "likelihood": str,
                    "impact": str,
                    "mitigation": str,
                    "owner": str,
                },
                ...
            ]
        }

    Escalation is computed here, not read from `data` - see escalation.py
    for why that decision was pulled out of the AI call entirely.
    """

    def build(self, data: dict):
        doc = self.document
        risks = data.get("risks", [])

        doc.add_heading("Risk Register", level=1)

        doc.add_heading("1. All Identified Risks", level=2)
        if not risks:
            doc.add_paragraph("No risks generated.")
        else:
            table = doc.add_table(rows=1, cols=5)
            table.style = "Table Grid"
            header = table.rows[0].cells
            header[0].text = "Risk"
            header[1].text = "Likelihood"
            header[2].text = "Impact"
            header[3].text = "Mitigation"
            header[4].text = "Owner"

            for r in risks:
                row = table.add_row().cells
                row[0].text = str(r.get("risk_description", ""))
                row[1].text = str(r.get("likelihood", ""))
                row[2].text = str(r.get("impact", ""))
                row[3].text = str(r.get("mitigation", ""))
                row[4].text = str(r.get("owner", ""))

        doc.add_heading("2. Escalation Summary", level=2)
        escalations = [
            r for r in risks
            if needs_escalation(r.get("likelihood", ""), r.get("impact", ""))
        ]

        if not escalations:
            doc.add_paragraph(
                "No risks meet the escalation threshold "
                "(High impact, or High likelihood with Medium-or-higher impact)."
            )
        else:
            doc.add_paragraph(
                "The following risks meet the escalation threshold and should "
                "be raised beyond the project team:"
            )
            for r in escalations:
                doc.add_paragraph(
                    f"{r.get('risk_description', '')} "
                    f"(Likelihood: {r.get('likelihood', '')}, "
                    f"Impact: {r.get('impact', '')}) — "
                    f"Owner: {r.get('owner', '')}",
                    style="List Bullet",
                )

from .base_generator import BaseGenerator


class StatusReportGenerator(BaseGenerator):
    """
    Builds a Status Report Word document. The document structure is
    identical regardless of audience - what actually differs is the
    *content* of `data`, because build_status_report_prompt() already
    steered the AI toward executive or team-level language before this
    class ever sees the result. This generator doesn't need to know or
    care which audience was chosen.

    Expected shape of `data`:
        {
            "report_title": str,
            "summary": str,
            "highlights": [str, ...],
            "risks_or_blockers": [str, ...],
            "next_steps": [str, ...],
        }
    """

    def build(self, data: dict):
        doc = self.document

        doc.add_heading(data.get("report_title", "Status Report"), level=1)

        doc.add_heading("Summary", level=2)
        doc.add_paragraph(data.get("summary", ""))

        doc.add_heading("Highlights", level=2)
        highlights = data.get("highlights", [])
        if not highlights:
            doc.add_paragraph("No highlights recorded.")
        else:
            for item in highlights:
                doc.add_paragraph(item, style="List Bullet")

        doc.add_heading("Risks & Blockers", level=2)
        risks = data.get("risks_or_blockers", [])
        if not risks:
            doc.add_paragraph("No risks or blockers reported.")
        else:
            for item in risks:
                doc.add_paragraph(item, style="List Bullet")

        doc.add_heading("Next Steps", level=2)
        next_steps = data.get("next_steps", [])
        if not next_steps:
            doc.add_paragraph("No next steps recorded.")
        else:
            for item in next_steps:
                doc.add_paragraph(item, style="List Bullet")

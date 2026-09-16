from .base_generator import BaseGenerator


class TimelineGenerator(BaseGenerator):
    """
    Builds a Milestones & Timeline Word document.

    Expected shape of `data`:
        {
            "project_name": str,
            "milestones": [
                {"phase_name": str, "milestone_name": str, "description": str},
                ...
            ],
            "sequencing_notes": [str, ...],
        }
    """

    def build(self, data: dict):
        doc = self.document

        doc.add_heading("Milestones & Timeline", level=1)
        doc.add_paragraph(f"Project: {data.get('project_name', 'Untitled Project')}")

        doc.add_heading("1. Milestones", level=2)
        milestones = data.get("milestones", [])
        if not milestones:
            doc.add_paragraph("No milestones generated.")
        else:
            table = doc.add_table(rows=1, cols=3)
            table.style = "Table Grid"
            header = table.rows[0].cells
            header[0].text = "Phase"
            header[1].text = "Milestone"
            header[2].text = "Description"

            for m in milestones:
                row = table.add_row().cells
                row[0].text = str(m.get("phase_name", ""))
                row[1].text = str(m.get("milestone_name", ""))
                row[2].text = str(m.get("description", ""))

        doc.add_heading("2. Scheduling Notes (parallel vs. sequential)", level=2)
        notes = data.get("sequencing_notes", [])
        if not notes:
            doc.add_paragraph("No scheduling notes generated.")
        else:
            for note in notes:
                doc.add_paragraph(note, style="List Bullet")

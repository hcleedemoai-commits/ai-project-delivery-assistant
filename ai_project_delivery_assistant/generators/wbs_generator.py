from .base_generator import BaseGenerator


class WBSGenerator(BaseGenerator):
    """
    Builds a Work Breakdown Structure Word document.

    Expected shape of `data`:
        {
            "project_name": str,
            "phases": [
                {
                    "phase_name": str,
                    "phase_goal": str,
                    "tasks": [
                        {"id": str, "description": str, "priority": str},
                        ...
                    ],
                },
                ...
            ],
        }
    """

    def build(self, data: dict):
        doc = self.document

        doc.add_heading("Work Breakdown Structure", level=1)
        doc.add_paragraph(f"Project: {data.get('project_name', 'Untitled Project')}")

        for phase_num, phase in enumerate(data.get("phases", []), start=1):
            phase_name = phase.get("phase_name", f"Phase {phase_num}")
            phase_goal = phase.get("phase_goal", "")

            doc.add_heading(f"Phase {phase_num}: {phase_name}", level=2)
            if phase_goal:
                doc.add_paragraph(phase_goal)

            tasks = phase.get("tasks", [])
            if not tasks:
                doc.add_paragraph("No tasks generated for this phase.")
                continue

            table = doc.add_table(rows=1, cols=3)
            table.style = "Table Grid"

            header = table.rows[0].cells
            header[0].text = "ID"
            header[1].text = "Task"
            header[2].text = "Priority"

            for task in tasks:
                row = table.add_row().cells
                row[0].text = str(task.get("id", ""))
                row[1].text = str(task.get("description", ""))
                row[2].text = str(task.get("priority", ""))

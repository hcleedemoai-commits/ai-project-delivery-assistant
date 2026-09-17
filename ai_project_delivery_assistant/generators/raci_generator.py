from .base_generator import BaseGenerator
from ..raci_rules import validate_raci


class RaciGenerator(BaseGenerator):
    """
    Builds a RACI Matrix Word document from the structured dict returned
    by AIResponseParser after calling build_raci_prompt().

    Expected shape of `data`:
        {
            "activities": [str, ...],
            "roles": [str, ...],
            "assignments": {activity: {role: "R"/"A"/"C"/"I"/""}, ...},
        }

    Validation warnings are computed here via raci_rules.validate_raci() -
    not read from `data` - so the document always shows whether the AI's
    matrix actually follows the one-Accountable-per-activity rule, rather
    than assuming it did because the prompt asked for it.
    """

    def build(self, data: dict):
        doc = self.document

        activities = data.get("activities", [])
        roles = data.get("roles", [])
        assignments = data.get("assignments", {})

        doc.add_heading("RACI Matrix", level=1)

        doc.add_heading("1. Matrix", level=2)
        if not activities or not roles:
            doc.add_paragraph("No RACI matrix generated.")
        else:
            table = doc.add_table(rows=1, cols=len(roles) + 1)
            table.style = "Table Grid"
            header = table.rows[0].cells
            header[0].text = "Activity"
            for i, role in enumerate(roles):
                header[i + 1].text = str(role)

            for activity in activities:
                row = table.add_row().cells
                row[0].text = str(activity)
                activity_assignments = assignments.get(activity, {})
                for i, role in enumerate(roles):
                    row[i + 1].text = str(activity_assignments.get(role, ""))

        doc.add_heading("2. Validation", level=2)
        warnings = validate_raci(activities, roles, assignments)
        if not warnings:
            doc.add_paragraph(
                "No issues found - every activity has exactly one Accountable "
                "owner and at least one Responsible role."
            )
        else:
            doc.add_paragraph(
                "The following issues were found and should be reviewed "
                "before this matrix is finalized:"
            )
            for w in warnings:
                doc.add_paragraph(w, style="List Bullet")

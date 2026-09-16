from .base_generator import BaseGenerator


class CharterGenerator(BaseGenerator):
    """
    Builds a Project Charter Word document from the structured dict
    returned by AIResponseParser after calling build_charter_prompt().

    Expected keys in `data`:
        project_name, business_objective, in_scope, out_of_scope,
        constraints, assumptions, stakeholders
    """

    def build(self, data: dict):
        doc = self.document

        doc.add_heading("Project Charter", level=1)

        doc.add_heading("1. Project Name", level=2)
        doc.add_paragraph(data.get("project_name", "Untitled Project"))

        doc.add_heading("2. Business Objective", level=2)
        doc.add_paragraph(data.get("business_objective", ""))

        doc.add_heading("3. In Scope", level=2)
        for item in data.get("in_scope", []):
            doc.add_paragraph(item, style="List Bullet")

        doc.add_heading("4. Out of Scope", level=2)
        for item in data.get("out_of_scope", []):
            doc.add_paragraph(item, style="List Bullet")

        doc.add_heading("5. Constraints", level=2)
        for item in data.get("constraints", []):
            doc.add_paragraph(item, style="List Bullet")

        doc.add_heading("6. Assumptions", level=2)
        for item in data.get("assumptions", []):
            doc.add_paragraph(item, style="List Bullet")

        doc.add_heading("7. Stakeholders", level=2)
        for item in data.get("stakeholders", []):
            doc.add_paragraph(item, style="List Bullet")

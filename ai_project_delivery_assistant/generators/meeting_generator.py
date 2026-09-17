from .base_generator import BaseGenerator


class MeetingMinutesGenerator(BaseGenerator):
    """
    Builds a Meeting Minutes Word document from two sources that were
    deliberately kept separate all the way through the pipeline:

    - `parsed` (from meeting_parser.parse_meeting_notes): {"date", "attendees"}
      - deterministic, taken from the notes' own header, never touched by the AI.
    - `ai_data` (from AIResponseParser after build_meeting_prompt()):
      {"discussion_summary", "decisions", "action_items"}
      - the AI's judgement about the free-text discussion.

    Kept as two separate parameters (not merged into one dict before this
    point) so it stays visible, right up to the call site in main.py,
    which fields came from code and which came from the AI.
    """

    def build(self, parsed: dict, ai_data: dict):
        doc = self.document

        doc.add_heading("Meeting Minutes", level=1)

        doc.add_heading("Meeting Details", level=2)
        doc.add_paragraph(f"Date: {parsed.get('date') or 'Not specified'}")
        attendees = parsed.get("attendees", [])
        doc.add_paragraph(
            f"Attendees: {', '.join(attendees) if attendees else 'Not specified'}"
        )

        doc.add_heading("1. Discussion Summary", level=2)
        doc.add_paragraph(ai_data.get("discussion_summary", ""))

        doc.add_heading("2. Decisions", level=2)
        decisions = ai_data.get("decisions", [])
        if not decisions:
            doc.add_paragraph("No decisions recorded.")
        else:
            for d in decisions:
                doc.add_paragraph(d, style="List Bullet")

        doc.add_heading("3. Action Items", level=2)
        action_items = ai_data.get("action_items", [])
        if not action_items:
            doc.add_paragraph("No action items recorded.")
        else:
            table = doc.add_table(rows=1, cols=3)
            table.style = "Table Grid"
            header = table.rows[0].cells
            header[0].text = "Action"
            header[1].text = "Owner"
            header[2].text = "Due"

            for item in action_items:
                row = table.add_row().cells
                row[0].text = str(item.get("description", ""))
                row[1].text = str(item.get("owner", ""))
                row[2].text = str(item.get("due_date", ""))

    def generate(self, parsed: dict, ai_data: dict, output_file: str):
        # Overrides BaseGenerator.generate() because this generator needs
        # two inputs, not one - build() below takes both, so the base
        # class's single-argument generate() doesn't fit this generator.
        self.build(parsed, ai_data)
        self.save(output_file)

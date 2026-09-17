"""
Deterministic preprocessing for raw meeting notes - the "parser" stage of
the parser -> AI analysis -> generator chain.

Meeting notes almost always start with a small header the note-taker
already wrote unambiguously (who was there, what date it was). Sending
that to the AI and asking it to extract it back out would burn a call on
something that's already explicit in the text, and risks the AI getting
a name wrong or dropping someone from the attendee list. So this module
pulls out only the parts that are already structured, in plain Python,
and leaves everything else (the actual discussion) as free text for the
AI to reason about - that's the part that genuinely needs judgement.
"""

import re


def parse_meeting_notes(raw_text: str) -> dict:
    """
    Expects (loosely) a header of "Date: ..." and "Attendees: ..." lines,
    in any order, followed by free-text discussion notes. Returns:
        {
            "date": str or None,
            "attendees": [str, ...],   # [] if no Attendees line found
            "body": str,               # everything that wasn't a header line
        }

    Deliberately forgiving: a note-taker who skips the header, writes it
    differently, or puts it mid-document still gets a usable "body" -
    they just don't get date/attendees pulled out, which downstream code
    already treats as optional.
    """
    date = None
    attendees = []
    body_lines = []

    for line in raw_text.splitlines():
        date_match = re.match(r"^\s*date\s*:\s*(.+)$", line, re.IGNORECASE)
        attendees_match = re.match(r"^\s*attendees\s*:\s*(.+)$", line, re.IGNORECASE)

        if date_match:
            date = date_match.group(1).strip()
        elif attendees_match:
            attendees = [
                name.strip()
                for name in attendees_match.group(1).split(",")
                if name.strip()
            ]
        else:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()

    return {"date": date, "attendees": attendees, "body": body}

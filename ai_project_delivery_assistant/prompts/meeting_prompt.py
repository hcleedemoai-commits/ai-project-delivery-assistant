def build_meeting_prompt(body_text: str) -> str:
    """
    Turns the free-text body of meeting notes (date and attendees already
    stripped out by meeting_parser.py) into a prompt asking the AI to act
    as a Business Analyst and extract a discussion summary, decisions,
    and action items - single-shot, same pattern as Charter and Risk
    Register.

    Only receives `body_text`, never the raw notes - the AI never sees
    (and therefore can't mangle) the date or attendee list, because that
    part was already handled deterministically before this prompt exists.
    """
    return f"""
You are a Business Analyst turning raw meeting notes into structured
minutes.

Meeting notes:
{body_text}

Extract:
1. A short discussion summary (2-4 sentences, what was actually talked
   about - not a restatement of every line).
2. The decisions that were made (only firm decisions, not open questions).
3. The action items that came out of the meeting.

For each action item, identify:
- description: what needs to be done
- owner: who is responsible (use the name as it appears in the notes; if
  genuinely unclear, use "Unassigned")
- due_date: if a date or timeframe was mentioned, otherwise "Not specified"

Return your answer as JSON only, with exactly these keys:
- discussion_summary (string)
- decisions (list of strings)
- action_items (list of objects, each with "description", "owner", "due_date")
""".strip()

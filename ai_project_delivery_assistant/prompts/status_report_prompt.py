AUDIENCES = ("Executive", "Team")

_AUDIENCE_INSTRUCTIONS = {
    "Executive": (
        "Write for a busy executive audience who has 30 seconds and cares "
        "about business impact, risk, and decisions they need to make - "
        "not implementation detail. Avoid technical jargon. Keep the "
        "summary to 2-3 sentences. Highlights and next steps should be "
        "outcome-focused (what changed for the business), not task-level."
    ),
    "Team": (
        "Write for the delivery team who already knows the technical "
        "context and wants specifics they can act on. Technical detail "
        "and task-level language are fine and expected. Highlights and "
        "next steps should name concrete work items, not just outcomes."
    ),
}


def build_status_report_prompt(project_status_text: str, audience: str) -> str:
    """
    Same underlying facts, two different prompts - the tone and level of
    detail are steered entirely by which _AUDIENCE_INSTRUCTIONS block gets
    interpolated in. This is prompt parameterization: one prompt template,
    audience as a variable, rather than hand-writing a second prompt from
    scratch for the Team version.

    `audience` must be one of AUDIENCES - main.py enforces this via a
    st.selectbox, so there's no free-text audience value to sanitize here.
    """
    instructions = _AUDIENCE_INSTRUCTIONS.get(audience, _AUDIENCE_INSTRUCTIONS["Team"])

    return f"""
You are a Project Manager writing a status report from the notes below.

{instructions}

Project status notes:
{project_status_text}

Return your answer as JSON only, with exactly these keys:
- report_title (string)
- summary (string)
- highlights (list of strings - progress made)
- risks_or_blockers (list of strings - empty list if none)
- next_steps (list of strings)
""".strip()

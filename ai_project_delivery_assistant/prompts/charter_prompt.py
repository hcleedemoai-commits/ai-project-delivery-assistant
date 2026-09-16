def build_charter_prompt(idea_text: str) -> str:
    """
    Turns a plain-language project idea into a prompt that asks the AI
    to act as a Senior PM and return a structured project charter as JSON.

    Kept in its own module (not inline in main.py) so this exact prompt
    is easy to test, tweak, and reuse from other places later - the same
    pattern as RequirementContextBuilder from the old project.
    """
    return f"""
You are a Senior Project Manager writing a project charter.

A stakeholder has described their project idea in plain language below.
Turn it into a structured project charter.

Project idea:
{idea_text}

Return your answer as JSON only, with exactly these keys:
- project_name (string)
- business_objective (string, 1-2 sentences)
- in_scope (list of strings)
- out_of_scope (list of strings)
- constraints (list of strings)
- assumptions (list of strings)
- stakeholders (list of strings)

If the idea doesn't give you enough information for a field, make a
reasonable, clearly-labeled assumption rather than leaving it empty.
""".strip()

def build_risk_prompt(idea_text: str) -> str:
    """
    Turns a plain-language project idea into a prompt that asks the AI to
    act as a Senior Risk Manager and return a structured risk register as
    JSON - one call, the same single-shot pattern as the Charter prompt.

    Deliberately does NOT ask the AI to decide which risks should be
    escalated. Escalation is a fixed business rule (see escalation.py) -
    something that must be applied the same way every time, which is a
    poor fit for an AI call that can phrase the same judgement two
    different ways on two different runs. The AI's job here is the part
    that genuinely needs judgement: reading a fuzzy project description
    and identifying realistic risks. The escalation decision is applied
    afterwards, in plain Python, on top of the AI's likelihood/impact.
    """
    return f"""
You are a Senior Risk Manager reviewing a project for delivery risks.

A stakeholder has described their project idea in plain language below.
Identify the realistic delivery risks and propose how to handle each one.

Project idea:
{idea_text}

For each risk, assess:
- likelihood: one of "Low", "Medium", "High"
- impact: one of "Low", "Medium", "High"
- mitigation: a concrete action to reduce the risk, not a vague platitude
- owner: a role (not a named person) who would realistically be
  accountable for watching this risk, e.g. "Project Manager",
  "Technical Lead", "Business Analyst"

Return your answer as JSON only, with exactly these keys:
- risks (list of objects, each with "risk_description", "likelihood",
  "impact", "mitigation", "owner")
""".strip()

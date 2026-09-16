def build_decision_prompt(idea_text: str) -> str:
    """
    Turns a plain-language description of a decision into a prompt asking
    the AI to act as a Senior Business Analyst and lay out a decision
    matrix: the realistic options, the criteria that matter, and a score
    for each option against each criterion - single-shot, the same
    pattern as the Charter and Risk Register prompts.

    Deliberately does NOT ask the AI to compute a weighted total or name
    a winner - see decision_matrix.py for why that arithmetic is done in
    plain Python afterwards instead of trusted to the model.
    """
    return f"""
You are a Senior Business Analyst helping a stakeholder think through a
decision, using a weighted decision matrix.

The stakeholder has described the decision in plain language below.
Identify the realistic options, the criteria that matter for choosing
between them, and score each option against each criterion.

Decision to analyze:
{idea_text}

Rules:
- Identify 2-4 realistic options (not a strawman option included only to
  make another option look better).
- Identify 3-5 criteria that would genuinely matter to this decision
  (e.g. cost, time to deliver, risk, maintainability - tailored to what
  was actually described, not a generic list).
- Give each criterion a weight from 1 (barely matters) to 10 (matters a
  lot), reflecting the stakeholder's likely priorities.
- Score every option against every criterion on a 1 (poor fit) to 5
  (excellent fit) scale, with a one-sentence rationale for each score.

Return your answer as JSON only, with exactly these keys:
- decision_context (string, 1 sentence restating what's being decided)
- options (list of strings)
- criteria (list of objects, each with "name" and "weight")
- scores (object keyed by option name; each value is an object keyed by
  criterion name; each of those values is an object with "score" and
  "rationale")
""".strip()

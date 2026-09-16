"""
Escalation-path logic: a fixed business rule for which risks need to be
raised above the project team, applied in plain Python - not left to the
AI to decide per-call.

Why this lives outside the AI call: likelihood/impact assessment benefits
from the AI reading the fuzzy project description, but "does this risk
get escalated" should give the exact same answer every time given the
same likelihood/impact, on any project, for any user. That's a rule, not
a judgement call - and rules belong in code that can be unit tested,
not in a prompt that might get phrased slightly differently by the model
from one run to the next.
"""

_SEVERITY = {"Low": 1, "Medium": 2, "High": 3}


def needs_escalation(likelihood: str, impact: str) -> bool:
    """
    A risk is escalation-worthy when:
    - both likelihood and impact are "High", or
    - impact alone is "High" (a high-impact risk is worth a second pair
      of eyes even if it's judged unlikely - "unlikely" is often wrong).

    Unrecognised values are treated as "Medium" (a safe middle default)
    rather than crashing the report - the AI's wording won't always
    exactly match "Low"/"Medium"/"High".
    """
    likelihood_score = _SEVERITY.get(likelihood, 2)
    impact_score = _SEVERITY.get(impact, 2)

    if impact_score == 3:
        return True
    if likelihood_score == 3 and impact_score >= 2:
        return True
    return False

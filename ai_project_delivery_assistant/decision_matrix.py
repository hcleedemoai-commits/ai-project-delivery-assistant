"""
Weighted decision matrix scoring - plain Python arithmetic, not trusted to
the AI, for the same reason escalation.py pulled the escalation decision
out of the risk prompt: an LLM asked to multiply and sum a table of
numbers can get the arithmetic wrong, and it won't get it wrong the same
way twice. The AI's real job here is the part that needs judgement - how
well does each option actually satisfy each criterion, and why. Once
those scores exist, turning them into a ranked recommendation is just
weighted-sum arithmetic, and arithmetic belongs in code that can be
tested against a known answer.
"""


def compute_weighted_totals(criteria: list, scores: dict) -> dict:
    """
    criteria: [{"name": str, "weight": number}, ...]
    scores:   {option_name: {criterion_name: {"score": number, ...}, ...}, ...}

    Returns {option_name: weighted_total (float)}, one entry per option in
    `scores`. A criterion or score that's missing or malformed contributes
    0 for that cell rather than raising - one bad cell shouldn't take down
    the whole matrix.
    """
    totals = {}

    for option_name, option_scores in scores.items():
        total = 0.0
        for criterion in criteria:
            name = criterion.get("name", "")
            weight = criterion.get("weight", 0) or 0
            cell = option_scores.get(name, {})
            score = cell.get("score", 0) or 0
            total += weight * score
        totals[option_name] = total

    return totals


def rank_options(totals: dict) -> list:
    """
    Returns [(option_name, weighted_total), ...] sorted highest total
    first. Ties keep the order the options were originally given in,
    since Python's sort is stable.
    """
    return sorted(totals.items(), key=lambda pair: pair[1], reverse=True)

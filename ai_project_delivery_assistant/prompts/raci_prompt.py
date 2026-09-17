def build_raci_prompt(idea_text: str) -> str:
    """
    Turns a plain-language project idea into a prompt asking the AI to
    act as a Senior Project Manager and lay out a RACI matrix - single
    shot, same pattern as Charter and Risk Register.

    The AI is asked to follow the "exactly one Accountable" rule as an
    instruction, but that instruction is not trusted blindly - see
    raci_rules.py, which checks the AI's actual answer against the same
    rule afterwards. Telling the model the rule usually gets it followed;
    it doesn't guarantee it, which is exactly why the check exists.
    """
    return f"""
You are a Senior Project Manager creating a RACI matrix for a project.

A stakeholder has described their project idea in plain language below.
Identify the key activities and the roles involved, then assign RACI
letters for each activity/role pair.

Project idea:
{idea_text}

Rules:
- Identify 4-7 key activities (delivery-level activities, not tiny tasks).
- Identify 3-5 roles realistically involved (e.g. "Project Manager",
  "Business Analyst", "Technical Lead", "Stakeholder" - tailored to what
  was actually described).
- For each activity, assign exactly one role as Accountable ("A") and at
  least one role as Responsible ("R"). Use "C" for Consulted, "I" for
  Informed, and "" (empty string) for roles not involved in that activity.

Return your answer as JSON only, with exactly these keys:
- activities (list of strings)
- roles (list of strings)
- assignments (object keyed by activity name; each value is an object
  keyed by role name, with a value of "R", "A", "C", "I", or "")
""".strip()

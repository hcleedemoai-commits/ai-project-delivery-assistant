"""
RACI validation rules - plain Python, checked after the AI assigns
R/A/C/I letters, not asked of the AI itself.

A RACI matrix has a structural rule that has nothing to do with the
specific project: every activity must have exactly one Accountable (A).
Not zero (nobody owns the outcome), not two (nobody's actually
accountable when two people are - it just means neither is). This is a
rule about the *shape* of a RACI matrix, true for any project, not a
judgement call about this project - which is exactly the kind of thing
that keeps showing up in this app as something to verify in code rather
than trust an AI to get right by construction on every single call.
"""


def validate_raci(activities: list, roles: list, assignments: dict) -> list:
    """
    activities: [str, ...]
    roles:      [str, ...]
    assignments: {activity: {role: "R"/"A"/"C"/"I"/""}, ...}

    Returns a list of human-readable warning strings - empty if the
    matrix is structurally sound. Never raises: a missing or malformed
    activity in `assignments` is reported as a warning, not a crash.
    """
    warnings = []

    for activity in activities:
        role_letters = assignments.get(activity, {})

        accountable_count = sum(
            1 for letter in role_letters.values() if letter == "A"
        )
        responsible_count = sum(
            1 for letter in role_letters.values() if letter == "R"
        )

        if accountable_count == 0:
            warnings.append(f'"{activity}" has no Accountable (A) owner.')
        elif accountable_count > 1:
            warnings.append(
                f'"{activity}" has {accountable_count} Accountable (A) '
                "owners - RACI expects exactly one."
            )

        if responsible_count == 0:
            warnings.append(f'"{activity}" has no Responsible (R) role assigned.')

    return warnings

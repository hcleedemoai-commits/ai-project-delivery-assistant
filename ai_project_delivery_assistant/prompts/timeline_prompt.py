import json


def build_timeline_prompt(project_name: str, phases: list) -> str:
    """
    Unlike the WBS prompts, this one is a single call - the input is
    already structured (the phases/tasks from the WBS step), so the model
    just has to reason over data it's given, not invent structure from
    scratch. No need to split this into multiple steps.
    """

    # Only send phase names/goals/task descriptions - keep the prompt lean,
    # the model doesn't need task IDs or priorities to reason about sequencing.
    lean_phases = [
        {
            "phase_name": p.get("phase_name", ""),
            "phase_goal": p.get("phase_goal", ""),
            "tasks": [t.get("description", "") for t in p.get("tasks", [])],
        }
        for p in phases
    ]

    return f"""
You are a Senior Project Manager proposing a delivery timeline.

Project: {project_name}

The project has already been broken down into these phases and tasks:
{json.dumps(lean_phases, indent=2)}

Based on this breakdown:
1. Propose one milestone per phase (a milestone marks that phase's completion).
2. Note which phases could realistically run in parallel with each other,
   and which must happen strictly in sequence, with a one-line reason each.

Return your answer as JSON only, with exactly these keys:
- milestones (list of objects, each with "phase_name", "milestone_name", "description")
- sequencing_notes (list of strings)
""".strip()

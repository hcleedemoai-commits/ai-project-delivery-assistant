"""
WBS (Work Breakdown Structure) generation uses two prompts, not one -
this is the "iterative / multi-turn prompting" pattern from the roadmap.

Step 1: ask for the major phases only (a shallow, high-level list).
Step 2: ask, per phase, for the detailed tasks inside it.

Asking for everything in a single prompt tends to produce a shallow,
generic list. Splitting it into "phases first, then tasks per phase"
mirrors how a PM actually thinks, and gives the model a smaller, more
focused job at each step.
"""


def build_wbs_phases_prompt(idea_text: str) -> str:
    return f"""
You are a Senior Project Manager breaking a project into major phases.

Project idea:
{idea_text}

List the major phases of this project, in delivery order. 4 to 6 phases
is typical - do not list individual tasks yet, only phases.

Return your answer as JSON only, with exactly this key:
- phases (list of objects, each with "phase_name" and "phase_goal")
""".strip()


def build_wbs_tasks_prompt(idea_text: str, phase_name: str, phase_goal: str) -> str:
    return f"""
You are a Senior Project Manager breaking one project phase into detailed tasks.

Overall project idea:
{idea_text}

The phase to break down:
Phase name: {phase_name}
Phase goal: {phase_goal}

List the concrete tasks needed to complete this phase. For each task,
give a short id (like "T1"), a one-line description, and a priority
(High, Medium, or Low).

Return your answer as JSON only, with exactly this key:
- tasks (list of objects, each with "id", "description", "priority")
""".strip()

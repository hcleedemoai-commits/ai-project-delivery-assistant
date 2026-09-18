"""
Thin wrapper around the Jira Cloud REST API - the second Phase 5
integration, turning Meeting Minutes' Action Items into real, trackable
Jira issues.

Why Action Items specifically, and not the Risk Register or the WBS:
an action item is something a real person already committed to out
loud in a meeting - it has an owner and (usually) a timeframe. That is
exactly what an issue tracker is for. A Risk Register entry is still
AI-drafted speculation until a person reviews it, and WBS tasks are
already tracked in the project schedule - pushing either of those into
Jira automatically would pollute a team's backlog with tickets nobody
actually decided to act on.

Built directly on `requests`, same reasoning as NotionClient: this app
only needs one call (create an issue), and plain HTTP keeps it obvious
exactly what's being sent - no SDK internals to dig through when
something goes wrong.

Jira's auth model is different from Notion's: instead of a single
Bearer token, Jira Cloud uses HTTP Basic Auth with the account's email
address and an API token as the "password".
"""

import requests

from ..config import Config

JIRA_API_VERSION = "3"

# Values that mean "nobody has filled this in yet" - checked in
# validate() so a forgotten placeholder fails with a clear message
# instead of a confusing 401/404 from Jira itself.
_PLACEHOLDER_VALUES = {
    None,
    "",
    "https://your-domain.atlassian.net",
    "your-email@example.com",
    "your-api-token-here",
    "your-project-key-here",
}


class JiraClient:
    """Creates one Jira issue per meeting Action Item."""

    def __init__(self):
        self.base_url = (Config.JIRA_BASE_URL or "").rstrip("/")
        self.email = Config.JIRA_EMAIL
        self.api_token = Config.JIRA_API_TOKEN
        self.project_key = Config.JIRA_PROJECT_KEY
        self.issue_type = Config.JIRA_ISSUE_TYPE or "Task"

    def validate(self):
        """Raise a clear error naming every missing/placeholder setting at once."""
        missing = []

        if self.base_url in _PLACEHOLDER_VALUES:
            missing.append("JIRA_BASE_URL")
        if self.email in _PLACEHOLDER_VALUES:
            missing.append("JIRA_EMAIL")
        if self.api_token in _PLACEHOLDER_VALUES:
            missing.append("JIRA_API_TOKEN")
        if self.project_key in _PLACEHOLDER_VALUES:
            missing.append("JIRA_PROJECT_KEY")

        if missing:
            raise ValueError(
                "Jira isn't configured yet - missing/placeholder: "
                f"{', '.join(missing)}. Add real values to .env "
                "(an API token can be created at "
                "https://id.atlassian.com/manage-profile/security/api-tokens)."
            )

    # ---- payload building --------------------------------------------

    @staticmethod
    def _description_doc(lines: list) -> dict:
        """
        Jira Cloud's REST API v3 requires `description` in Atlassian
        Document Format (ADF) - a nested JSON structure, not a plain
        string. Each line becomes its own paragraph.
        """
        return {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": line}]}
                for line in lines
            ],
        }

    def _issue_payload(self, item: dict, meeting_date) -> dict:
        """
        `item` is one entry from Meeting Minutes' `action_items`:
            {"description": str, "owner": str, "due_date": str}
        (see MeetingMinutesGenerator's docstring for the full shape).

        The AI's `due_date` is free text ("next Friday", "Not
        specified") rather than a strict ISO date, so it's written into
        the description instead of Jira's own `duedate` field - that
        field rejects anything that isn't exactly YYYY-MM-DD, and
        failing every issue over an unparseable date would defeat the
        point of this integration.
        """
        description = item.get("description") or "(no description provided)"
        owner = item.get("owner") or "Unassigned"
        due_date = item.get("due_date") or "Not specified"

        # Jira's summary field has a hard 255-character limit.
        summary = description if len(description) <= 250 else description[:247] + "..."

        return {
            "fields": {
                "project": {"key": self.project_key},
                "issuetype": {"name": self.issue_type},
                "summary": summary,
                "description": self._description_doc(
                    [
                        f"Owner: {owner}",
                        f"Due: {due_date}",
                        f"From meeting on: {meeting_date or 'Not specified'}",
                    ]
                ),
            }
        }

    # ---- public API ----------------------------------------------------

    def push_meeting_action_items(self, parsed: dict, ai_data: dict) -> dict:
        """
        Creates one Jira issue per action item in `ai_data["action_items"]`.
        `parsed` is the deterministic {"date", "attendees", "body"} from
        meeting_parser.parse_meeting_notes() - only its "date" is used
        here, to note which meeting each issue came from.

        Unlike NotionClient.push_status_report() (one call, all-or-
        nothing), this makes one Jira API call *per* action item, so a
        single bad item (e.g. a project misconfiguration caught mid-run)
        shouldn't discard issues that were already created successfully.
        Returns a summary instead of raising on partial failure:
            {"status": "ok" | "partial" | "no_action_items",
             "created": ["PROJ-123", ...], "failed": [{"item": ..., "error": ...}, ...]}
        Only raises (ValueError) when Jira isn't configured at all -
        that's a setup problem, not a per-item one.
        """
        self.validate()

        action_items = ai_data.get("action_items", [])
        if not action_items:
            return {"status": "no_action_items", "created": [], "failed": []}

        url = f"{self.base_url}/rest/api/{JIRA_API_VERSION}/issue"
        meeting_date = parsed.get("date")

        created = []
        failed = []

        for item in action_items:
            payload = self._issue_payload(item, meeting_date)

            response = requests.post(
                url,
                auth=(self.email, self.api_token),
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=15,
            )

            if response.status_code == 201:
                created.append(response.json().get("key"))
            else:
                failed.append(
                    {
                        "item": item.get("description", ""),
                        "error": f"{response.status_code}: {response.text}",
                    }
                )

        return {
            "status": "ok" if not failed else "partial",
            "created": created,
            "failed": failed,
        }

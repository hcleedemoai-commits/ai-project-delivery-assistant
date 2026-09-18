"""
Offline tests for the Phase 5 Jira integration - no real API token or
network call needed. Jira's own API is mocked out with unittest.mock so
these tests check *this app's* logic (payload-building, validation,
partial-failure handling), not Jira's servers. Run with: pytest
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_project_delivery_assistant.integrations.jira_client import JiraClient


SAMPLE_PARSED = {
    "date": "2026-09-17",
    "attendees": ["Alice", "Bob", "Carol"],
    "body": "Discussed the login flow.",
}

SAMPLE_AI_DATA = {
    "discussion_summary": "Discussed the customer portal login flow.",
    "decisions": ["Use the existing internal SSO instead of a new login system."],
    "action_items": [
        {
            "description": "Confirm SSO API access with IT",
            "owner": "Alice",
            "due_date": "next Friday",
        },
        {
            "description": "Draft the updated login wireframes",
            "owner": "Carol",
            "due_date": "Not specified",
        },
    ],
}


def _client_with(base_url, email, api_token, project_key, issue_type="Task"):
    client = JiraClient()
    client.base_url = base_url
    client.email = email
    client.api_token = api_token
    client.project_key = project_key
    client.issue_type = issue_type
    return client


def _real_looking_client():
    return _client_with(
        "https://acme.atlassian.net", "pm@acme.com", "a_real_looking_token", "PMO"
    )


def test_validate_rejects_placeholder_base_url():
    client = _client_with(
        "https://your-domain.atlassian.net", "pm@acme.com", "tok", "PMO"
    )
    try:
        client.validate()
        assert False, "expected a ValueError"
    except ValueError as e:
        assert "JIRA_BASE_URL" in str(e)


def test_validate_reports_every_missing_field_at_once():
    client = _client_with(None, None, None, None)
    try:
        client.validate()
        assert False, "expected a ValueError"
    except ValueError as e:
        message = str(e)
        assert "JIRA_BASE_URL" in message
        assert "JIRA_EMAIL" in message
        assert "JIRA_API_TOKEN" in message
        assert "JIRA_PROJECT_KEY" in message


def test_validate_passes_with_real_looking_values():
    _real_looking_client().validate()  # should not raise


def test_issue_payload_includes_project_issuetype_and_summary():
    client = _real_looking_client()
    payload = client._issue_payload(
        {"description": "Confirm SSO API access with IT", "owner": "Alice", "due_date": "next Friday"},
        "2026-09-17",
    )

    assert payload["fields"]["project"]["key"] == "PMO"
    assert payload["fields"]["issuetype"]["name"] == "Task"
    assert payload["fields"]["summary"] == "Confirm SSO API access with IT"


def test_issue_payload_puts_owner_due_date_and_meeting_date_in_description():
    client = _real_looking_client()
    payload = client._issue_payload(
        {"description": "Draft wireframes", "owner": "Carol", "due_date": "Not specified"},
        "2026-09-17",
    )

    description_text = str(payload["fields"]["description"])
    assert "Carol" in description_text
    assert "Not specified" in description_text
    assert "2026-09-17" in description_text


def test_issue_payload_truncates_long_descriptions_to_fit_jiras_summary_limit():
    client = _real_looking_client()
    long_description = "A" * 300
    payload = client._issue_payload({"description": long_description}, "2026-09-17")

    assert len(payload["fields"]["summary"]) <= 250 + 3  # allows for the "..." suffix
    assert payload["fields"]["summary"].endswith("...")


def test_push_meeting_action_items_returns_no_action_items_status_when_list_is_empty():
    client = _real_looking_client()
    result = client.push_meeting_action_items(SAMPLE_PARSED, {"action_items": []})

    assert result["status"] == "no_action_items"
    assert result["created"] == []


@patch("ai_project_delivery_assistant.integrations.jira_client.requests.post")
def test_push_meeting_action_items_creates_one_issue_per_action_item(mock_post):
    mock_post.side_effect = [
        MagicMock(status_code=201, json=lambda: {"key": "PMO-101"}),
        MagicMock(status_code=201, json=lambda: {"key": "PMO-102"}),
    ]

    client = _real_looking_client()
    result = client.push_meeting_action_items(SAMPLE_PARSED, SAMPLE_AI_DATA)

    assert result["status"] == "ok"
    assert result["created"] == ["PMO-101", "PMO-102"]
    assert result["failed"] == []
    assert mock_post.call_count == 2


@patch("ai_project_delivery_assistant.integrations.jira_client.requests.post")
def test_push_meeting_action_items_reports_partial_failure_without_losing_successes(mock_post):
    mock_post.side_effect = [
        MagicMock(status_code=201, json=lambda: {"key": "PMO-101"}),
        MagicMock(status_code=400, text="issuetype: cannot be blank"),
    ]

    client = _real_looking_client()
    result = client.push_meeting_action_items(SAMPLE_PARSED, SAMPLE_AI_DATA)

    assert result["status"] == "partial"
    assert result["created"] == ["PMO-101"]
    assert len(result["failed"]) == 1
    assert "400" in result["failed"][0]["error"]


def test_push_meeting_action_items_refuses_to_call_jira_when_unconfigured():
    client = _client_with(None, None, None, None)
    try:
        client.push_meeting_action_items(SAMPLE_PARSED, SAMPLE_AI_DATA)
        assert False, "expected a ValueError"
    except ValueError:
        pass

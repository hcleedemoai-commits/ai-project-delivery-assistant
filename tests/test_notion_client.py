"""
Offline tests for the Phase 5 Notion integration - no real API key or
network call needed. Notion's own API is mocked out with unittest.mock
so these tests check *this app's* logic (block-building, validation,
error handling), not Notion's servers. Run with: pytest
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_project_delivery_assistant.integrations.notion_client import NotionClient


SAMPLE_STATUS_DATA = {
    "report_title": "Customer Portal - Week 6 Status",
    "summary": "The portal is broadly on track, with one schedule risk on invoicing.",
    "highlights": ["Login flow complete and in QA"],
    "risks_or_blockers": ["Invoicing API is undocumented, causing a delay"],
    "next_steps": ["Finish reverse-engineering the invoicing API"],
}


def _client_with(api_key, page_id):
    client = NotionClient()
    client.api_key = api_key
    client.page_id = page_id
    return client


def test_validate_rejects_missing_api_key():
    client = _client_with(None, "some-page-id")
    try:
        client.validate()
        assert False, "expected a ValueError"
    except ValueError as e:
        assert "NOTION_API_KEY" in str(e)


def test_validate_rejects_placeholder_api_key():
    client = _client_with("ntn_dummy_placeholder_replace_me", "some-page-id")
    try:
        client.validate()
        assert False, "expected a ValueError"
    except ValueError as e:
        assert "NOTION_API_KEY" in str(e)


def test_validate_rejects_missing_page_id():
    client = _client_with("ntn_a_real_looking_secret", None)
    try:
        client.validate()
        assert False, "expected a ValueError"
    except ValueError as e:
        assert "NOTION_PAGE_ID" in str(e)


def test_validate_passes_with_real_looking_values():
    client = _client_with("ntn_a_real_looking_secret", "some-page-id")
    client.validate()  # should not raise


def test_status_report_blocks_include_title_and_summary():
    client = _client_with("ntn_a_real_looking_secret", "some-page-id")
    blocks = client._status_report_blocks(SAMPLE_STATUS_DATA)

    block_text = str(blocks)
    assert "Customer Portal - Week 6 Status" in block_text
    assert "invoicing" in block_text


def test_status_report_blocks_use_bulleted_list_items_for_highlights():
    client = _client_with("ntn_a_real_looking_secret", "some-page-id")
    blocks = client._status_report_blocks(SAMPLE_STATUS_DATA)

    bullet_texts = [
        b["bulleted_list_item"]["rich_text"][0]["text"]["content"]
        for b in blocks
        if b["type"] == "bulleted_list_item"
    ]
    assert "Login flow complete and in QA" in bullet_texts
    assert "Invoicing API is undocumented, causing a delay" in bullet_texts
    assert "Finish reverse-engineering the invoicing API" in bullet_texts


def test_status_report_blocks_handle_missing_data_gracefully():
    client = _client_with("ntn_a_real_looking_secret", "some-page-id")
    blocks = client._status_report_blocks({})

    block_text = str(blocks)
    assert "No summary recorded." in block_text
    assert "No highlights recorded." in block_text
    assert "No risks or blockers reported." in block_text
    assert "No next steps recorded." in block_text


@patch("ai_project_delivery_assistant.integrations.notion_client.requests.patch")
def test_push_status_report_calls_notion_api_and_reports_blocks_added(mock_patch):
    mock_response = MagicMock(status_code=200)
    mock_patch.return_value = mock_response

    client = _client_with("ntn_a_real_looking_secret", "some-page-id")
    result = client.push_status_report(SAMPLE_STATUS_DATA)

    assert result["status"] == "ok"
    assert result["blocks_added"] > 0
    mock_patch.assert_called_once()

    # sanity-check the call went to the right page's children endpoint
    called_url = mock_patch.call_args.args[0]
    assert called_url == "https://api.notion.com/v1/blocks/some-page-id/children"


@patch("ai_project_delivery_assistant.integrations.notion_client.requests.patch")
def test_push_status_report_raises_runtime_error_on_notion_failure(mock_patch):
    mock_response = MagicMock(status_code=401, text="Unauthorized")
    mock_patch.return_value = mock_response

    client = _client_with("ntn_a_real_looking_secret", "some-page-id")
    try:
        client.push_status_report(SAMPLE_STATUS_DATA)
        assert False, "expected a RuntimeError"
    except RuntimeError as e:
        assert "401" in str(e)


def test_push_status_report_refuses_to_call_notion_when_unconfigured():
    client = _client_with(None, None)
    try:
        client.push_status_report(SAMPLE_STATUS_DATA)
        assert False, "expected a ValueError"
    except ValueError:
        pass

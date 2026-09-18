"""
Thin wrapper around the Notion REST API - the Phase 5 stretch goal of
pushing a generated Status Report onto a live Notion page, instead of
(or alongside) the .docx file this app already produces.

Built directly on `requests` rather than the official `notion-client`
SDK on purpose: the API surface this app needs is a single call
(append blocks to a page), and writing that out in plain HTTP keeps it
obvious exactly what's being sent, with no SDK internals to dig through
when something goes wrong.

Notion's content model is "blocks", not paragraphs of text - a heading
is a block, a paragraph is a block, a bullet-list item is a block. This
client's only real job is translating the same `data` dict the docx
StatusReportGenerator already uses (see that class's docstring) into
that block format, then sending it to Notion. Same input, two outputs,
one source of truth.
"""

import requests

from ..config import Config

NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"

# Values that mean "nobody has put a real key here yet" - checked in
# validate() so a forgotten placeholder fails with a clear message
# instead of a confusing 401 from Notion itself.
_PLACEHOLDER_KEYS = {
    None,
    "",
    "your-api-key-here",
    "paste-your-integration-secret-here",
    "ntn_dummy_placeholder_replace_me",
}


class NotionClient:
    """Pushes generated report data to a single, pre-shared Notion page."""

    def __init__(self):
        self.api_key = Config.NOTION_API_KEY
        self.page_id = Config.NOTION_PAGE_ID

    def validate(self):
        """Raise a clear error if Notion isn't configured yet."""
        if self.api_key in _PLACEHOLDER_KEYS:
            raise ValueError(
                "NOTION_API_KEY not set. Add your Internal Integration Secret "
                "to .env - get one at https://www.notion.so/my-integrations"
            )

        if not self.page_id:
            raise ValueError(
                "NOTION_PAGE_ID not set. Add the page ID (from the page's "
                "URL) to .env."
            )

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }

    # ---- block builders --------------------------------------------
    # Each one returns a single Notion "block" dict. Kept as small
    # static helpers so _status_report_blocks() below reads like an
    # outline of the report, not a wall of nested dicts.

    @staticmethod
    def _heading_block(text: str, level: int = 2) -> dict:
        heading_type = {1: "heading_1", 2: "heading_2", 3: "heading_3"}.get(
            level, "heading_2"
        )
        return {
            "object": "block",
            "type": heading_type,
            heading_type: {"rich_text": [{"type": "text", "text": {"content": text}}]},
        }

    @staticmethod
    def _paragraph_block(text: str) -> dict:
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
        }

    @staticmethod
    def _bullet_block(text: str) -> dict:
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            },
        }

    @staticmethod
    def _divider_block() -> dict:
        return {"object": "block", "type": "divider", "divider": {}}

    def _status_report_blocks(self, data: dict) -> list:
        """
        Same `data` shape as StatusReportGenerator.build():
            {
                "report_title": str,
                "summary": str,
                "highlights": [str, ...],
                "risks_or_blockers": [str, ...],
                "next_steps": [str, ...],
            }

        A leading divider marks where each new report starts, since
        every push appends to the same page rather than replacing it -
        the page becomes a running log of reports over time.
        """
        blocks = [
            self._divider_block(),
            self._heading_block(data.get("report_title", "Status Report"), level=1),
            self._heading_block("Summary", level=2),
            self._paragraph_block(data.get("summary") or "No summary recorded."),
            self._heading_block("Highlights", level=2),
        ]

        highlights = data.get("highlights", [])
        if not highlights:
            blocks.append(self._paragraph_block("No highlights recorded."))
        else:
            blocks.extend(self._bullet_block(item) for item in highlights)

        blocks.append(self._heading_block("Risks & Blockers", level=2))
        risks = data.get("risks_or_blockers", [])
        if not risks:
            blocks.append(self._paragraph_block("No risks or blockers reported."))
        else:
            blocks.extend(self._bullet_block(item) for item in risks)

        blocks.append(self._heading_block("Next Steps", level=2))
        next_steps = data.get("next_steps", [])
        if not next_steps:
            blocks.append(self._paragraph_block("No next steps recorded."))
        else:
            blocks.extend(self._bullet_block(item) for item in next_steps)

        return blocks

    # ---- public API --------------------------------------------------

    def push_status_report(self, data: dict) -> dict:
        """
        Appends a Status Report to the configured Notion page as new
        blocks. Returns {"status": "ok", "blocks_added": N} on success;
        raises RuntimeError with Notion's own error message on failure,
        since a bare requests exception won't say *why* Notion rejected
        the call (wrong page ID, integration not shared with the page,
        malformed block, expired key, etc).
        """
        self.validate()

        blocks = self._status_report_blocks(data)
        url = f"{NOTION_BASE_URL}/blocks/{self.page_id}/children"

        # Notion caps each append call at 100 blocks. A single status
        # report is nowhere near that, but chunking here means this
        # method won't quietly break if the app ever pushes something
        # much longer.
        for i in range(0, len(blocks), 100):
            chunk = blocks[i : i + 100]
            response = requests.patch(
                url, headers=self._headers(), json={"children": chunk}, timeout=15
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Notion API error ({response.status_code}): {response.text}"
                )

        return {"status": "ok", "blocks_added": len(blocks)}

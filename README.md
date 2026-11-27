# ai-project-delivery-assistant

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Claude](https://img.shields.io/badge/Claude-Anthropic%20API-orange)](https://www.anthropic.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io/)
[![CI](https://github.com/hcleedemoai-commits/ai-project-delivery-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/hcleedemoai-commits/ai-project-delivery-assistant/actions/workflows/ci.yml)

## Overview

An AI-powered assistant for IT Project Managers and Business Systems Analysts.
It takes plain-language project input and turns it into structured, usable
project documentation - project charters, work breakdown structures,
milestone timelines, risk registers, decision matrices, meeting minutes,
audience-aware status reports, and RACI matrices - each backed by a real
Claude API call, not a template with blanks filled in.

Phase 5 goes one step further: instead of stopping at a downloaded `.docx`,
generated content can be pushed straight into the tools teams already use -
a Status Report onto a live Notion page, and Meeting Minutes' Action Items
as real Jira issues.

**Status: Phase 5 of 5 (in progress)** - Phases 1-4 are complete, and Phase 5's
external integrations (Notion + Jira) are built and working end to end. See
`ROADMAP.md` for the full 5-phase build plan and what's left.

## Project Structure

```
.
├── .env                                        # API configuration (not in git)
├── .gitignore                                  # Excluded files
├── LICENSE                                     # MIT License
├── README.md                                   # This file
├── ROADMAP.md                                  # 5-phase build plan
├── requirements.txt                            # Python dependencies
├── sample_data/                                # Sample input files
├── reports/                                    # Generated .docx outputs (git-ignored)
├── ai_project_delivery_assistant/
│   ├── __init__.py
│   ├── config.py                               # Configuration + provider/integration validation
│   ├── main.py                                 # Streamlit app (entry point, one tab per feature)
│   ├── meeting_parser.py                       # Deterministic Date/Attendees parsing (no AI call)
│   ├── raci_rules.py                           # RACI's one-Accountable rule, checked in code
│   ├── decision_matrix.py                      # Weighted-score computation, done in code not by the AI
│   ├── escalation.py                           # Fixed escalation rule for high-severity risks
│   ├── ai_engine/
│   │   ├── base_ai.py                          # Provider interface
│   │   ├── claude_ai.py                        # Real Claude (Anthropic) provider
│   │   ├── openrouter_ai.py                    # Optional alternate provider
│   │   ├── mock_ai.py                          # Offline/no-API-key provider
│   │   ├── ai_factory.py                       # Picks the provider from .env
│   │   └── response_parser.py                  # Turns AI text into structured JSON
│   ├── prompts/                                # One prompt-builder per feature
│   │   ├── charter_prompt.py
│   │   ├── wbs_prompt.py
│   │   ├── timeline_prompt.py
│   │   ├── risk_prompt.py
│   │   ├── decision_prompt.py
│   │   ├── meeting_prompt.py
│   │   ├── status_report_prompt.py
│   │   └── raci_prompt.py
│   ├── generators/                             # One .docx builder per feature
│   │   ├── base_generator.py
│   │   ├── charter_generator.py
│   │   ├── wbs_generator.py
│   │   ├── timeline_generator.py
│   │   ├── risk_generator.py
│   │   ├── decision_generator.py
│   │   ├── meeting_generator.py
│   │   ├── status_report_generator.py
│   │   └── raci_generator.py
│   └── integrations/                           # Phase 5: pushing content to external tools
│       ├── notion_client.py                    # Status Report -> a live Notion page
│       └── jira_client.py                      # Meeting Action Items -> real Jira issues
└── tests/                                      # Offline tests - no API key or network needed
    ├── test_ai_engine.py
    ├── test_charter.py
    ├── test_wbs.py
    ├── test_timeline.py
    ├── test_risk.py
    ├── test_decision.py
    ├── test_meeting.py
    ├── test_status_report.py
    ├── test_raci.py
    ├── test_notion_client.py
    └── test_jira_client.py
```

## Quick Start

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd ai-project-delivery-assistant
```

### 2. Set up a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Edit `.env` and set:

```env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your-real-key-here
```

Get a key at [console.anthropic.com](https://console.anthropic.com/). No key
yet? Set `AI_PROVIDER=mock` to try the app with canned responses instead.

### 5. (Optional) Configure the Notion and Jira integrations

Only needed for the Phase 5 "Push to Notion" / "Push Action Items to Jira"
buttons - every other feature works without these.

```env
# Notion - get a secret at https://www.notion.so/my-integrations,
# share the target page with that integration, and take the page ID
# from its URL
NOTION_API_KEY=ntn_your-real-secret-here
NOTION_PAGE_ID=your-32-character-page-id

# Jira - get an API token at
# https://id.atlassian.com/manage-profile/security/api-tokens
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-jira-account-email
JIRA_API_TOKEN=your-real-api-token-here
JIRA_PROJECT_KEY=your-project-key
JIRA_ISSUE_TYPE=Task
```

### 6. Run the app

```bash
streamlit run ai_project_delivery_assistant/main.py
```

### 7. Run the offline tests (optional, no API key needed)

```bash
pytest tests/
```

## Design notes

- **Provider abstraction**: every AI backend (`ClaudeAI`, `OpenRouterAI`,
  `MockAI`) implements the same `BaseAI.generate()` interface, so switching
  providers is a one-line change in `.env` - never a code change.
- **Fail loud, fail early**: `Config.validate()` raises a clear error the
  moment a required API key is missing, instead of failing deep inside an
  API call.
- **Code decides the rules, the AI decides the content**: several features
  split "what the AI drafts" from "what a fixed rule checks" - RACI's
  one-Accountable-owner rule (`raci_rules.py`), risk escalation
  (`escalation.py`), and decision-matrix scoring (`decision_matrix.py`) are
  all plain Python, so the same input always produces the same structural
  verdict regardless of what the AI happened to say.
- **One data shape, multiple destinations**: `StatusReportGenerator` (docx)
  and `NotionClient.push_status_report()` both consume the exact same
  `status_data` dict the AI produces - there's no second source of truth
  to drift between the file you download and the page you push.

## Responsible use

This tool produces AI-generated drafts of project documentation. It is meant
to accelerate a PM/BA's first pass, not replace their judgment - every
generated requirement analysis, risk, charter, or report should be reviewed
by a human before it's shared with stakeholders or acted on.

**Data handling**: no proprietary or client-confidential data should be
pasted into the app while using a third-party AI provider (Claude or
OpenRouter) unless that provider's data policy has been checked. The same
applies, doubly, once Phase 5's integrations are in play - pushing content
to Notion or Jira means it now exists as a real record in a third-party
system, not just a local file you control. Check both services' data
policies before pushing anything sensitive, and treat API tokens (in
`.env`, never committed to git) with the same care as a password.

**What gets automated, and what doesn't**: the two Phase 5 integrations
were deliberately scoped narrower than "push everything everywhere."
Meeting Action Items are pushed to Jira as real issues because they're
concrete commitments someone already made out loud in the meeting - but the
Risk Register is *not* wired to auto-create Jira tickets, because a
generated risk is still AI-drafted speculation until a person reviews it;
auto-creating tickets from it would let unconfirmed, possibly-wrong items
into a team's real backlog, undermining the tracker's usefulness for
everyone. In general: the closer an AI output gets to creating a
side-effect in a system other people rely on (a ticket, a shared page, an
email), the more that step deserves a human "yes, send this" in the loop
rather than being fully automatic - which is why every push in this app is
a separate, deliberate button click, never something that fires
automatically after generation.

**Review before you push**: the "Push to Notion" and "Push Action Items to
Jira" buttons send exactly what's shown in the preview above them - always
read that preview first. A pushed Notion block or created Jira issue isn't
silently undone by re-generating the report; if something was wrong, it
needs to be corrected or removed directly in Notion/Jira.

## License

MIT License - see `LICENSE`.

## Author

**HwangChin**
- GitHub: [your-github-url-here](your-github-url-here)

---
Star this repository if you find it useful!

# ai-project-delivery-assistant

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Claude](https://img.shields.io/badge/Claude-Anthropic%20API-orange)](https://www.anthropic.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io/)

## Overview

An AI-powered assistant for IT Project Managers and Business Systems Analysts.
It takes plain-language project input and turns it into structured, usable
project documentation - starting with requirement analysis, and growing
module by module toward charters, WBS, risk registers, and stakeholder
reports.

**Status: Phase 1 of 5** - the app is wired end to end to a real Claude call
and can return structured JSON analysis. See `ROADMAP.md` for the full
5-phase build plan and what's coming next.

## Project Structure

```
.
├── .env                                    # API configuration (not in git)
├── .gitignore                              # Excluded files
├── LICENSE                                 # MIT License
├── README.md                               # This file
├── ROADMAP.md                              # 5-phase build plan
├── requirements.txt                        # Python dependencies
├── sample_data/                            # Sample input files
│   └── (your data here)
├── reports/                                # Generated outputs (git-ignored)
├── ai_project_delivery_assistant/
│   ├── __init__.py
│   ├── config.py                           # Configuration + provider validation
│   ├── main.py                             # Streamlit app (entry point)
│   └── ai_engine/
│       ├── __init__.py
│       ├── base_ai.py                      # Provider interface
│       ├── claude_ai.py                    # Real Claude (Anthropic) provider
│       ├── openrouter_ai.py                # Optional alternate provider
│       ├── mock_ai.py                      # Offline/no-API-key provider
│       ├── ai_factory.py                   # Picks the provider from .env
│       └── response_parser.py              # Turns AI text into structured JSON
└── tests/
    └── test_ai_engine.py                   # Offline smoke tests (no API key needed)
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

### 5. Run the app

```bash
streamlit run ai_project_delivery_assistant/main.py
```

### 6. Run the offline tests (optional, no API key needed)

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

## Responsible use

This tool produces AI-generated drafts of project documentation. It is meant
to accelerate a PM/BA's first pass, not replace their judgment - every
generated requirement analysis, risk, or report should be reviewed by a
human before it's shared with stakeholders or acted on. No proprietary or
client-confidential data should be pasted into the app while using a
third-party AI provider (OpenRouter) unless that provider's data policy has
been checked.

## License

MIT License - see `LICENSE`.

## Author

**HwangChin**
- GitHub: [your-github-url-here](your-github-url-here)

---
Star this repository if you find it useful!

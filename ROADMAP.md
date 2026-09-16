# Rebuild Roadmap

Five phases, each mapped to a module of the Claude-for-Project-Managers
curriculum. Every phase ends with something that works end to end in the
browser before the next one starts.

**Ground rules**

1. Build vertically, not horizontally - finish one feature end to end
   (upload to download) before starting the next.
2. Real AI from day one - the actual Claude API key is wired in from the
   first commit, never a mock-only detour.

## Phase 1 - Plumbing & Prompting Foundations (Module 1) ✅

- [x] Scaffold the project (Streamlit app, `.env`, complete `requirements.txt`)
- [x] One `ClaudeAI` wrapper class calling the real Anthropic API
- [x] Smallest working loop: prompt in, raw response shown in the browser
- [x] Upgraded prompt requesting structured JSON, parsed on return

## Phase 2 - Planning & Scoping (Module 2)

- [ ] Project Charter generator (plain-language idea -> objectives/scope/constraints -> Word doc)
- [ ] Work Breakdown Structure generator via iterative prompting
- [ ] Milestone & timeline outline generator

## Phase 3 - Risk & Decision Analysis (Module 3)

- [ ] Risk Register generator (likelihood, impact, mitigation, owner)
- [ ] Escalation-path logic for high-severity risks
- [ ] Decision matrix / trade-off generator

## Phase 4 - Reporting & Stakeholder Communication (Module 4)

- [ ] Meeting-minutes chain (parser -> AI analysis -> Word generator), wired into the app
- [ ] Executive status-report generator
- [ ] RACI matrix generator
- [ ] Audience/tone selector (executive vs. team)

## Phase 5 - Integration, Responsible Use & Capstone (Module 5)

- [ ] Responsible Use section in the README
- [ ] Stretch: one external tool integration (Jira or Notion API)
- [ ] Capstone run: plain-language idea -> charter -> WBS -> risk register -> status report, all as real documents

---
An interactive, checkable version of this roadmap is also tracked separately
outside this repo.

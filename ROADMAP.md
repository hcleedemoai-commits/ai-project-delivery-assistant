# Rebuild Roadmap

Five phases, each built around one real PM problem worth solving. Every phase
ends with something that works end to end in the browser before the next one
starts. Pair this with the Concepts & Value Notebook (tracked separately)
for the why/how/business-value behind each phase, and an interview-ready
pitch line for each one.

**Ground rules**

1. Build vertically, not horizontally - finish one feature end to end
   (upload to download) before starting the next.
2. Real AI from day one - the actual Claude API key is wired in from the
   first commit, never a mock-only detour.

## Phase 1 - Foundations: Proving the Wire Works ✅

- [x] Scaffold the project (Streamlit app, `.env`, complete `requirements.txt`)
- [x] One `ClaudeAI` wrapper class calling the real Anthropic API
- [x] Smallest working loop: prompt in, raw response shown in the browser
- [x] Upgraded prompt requesting structured JSON, parsed on return

## Phase 2 - Planning & Scoping: From Paragraph to Plan ✅

- [x] Project Charter generator (plain-language idea -> objectives/scope/constraints -> Word doc)
- [x] Work Breakdown Structure generator via iterative prompting (phases, then tasks per phase)
- [x] Milestone & timeline outline generator (builds on the WBS via `st.session_state`, flags parallel vs. sequential phases)

## Phase 3 - Risk & Decision Analysis: Reasoning Under Uncertainty ✅

- [x] Risk Register generator (likelihood, impact, mitigation, owner)
- [x] Escalation-path logic for high-severity risks (a fixed rule in code, not left to the AI)
- [x] Decision matrix / trade-off generator (AI scores options, Python computes the weighted result)

## Phase 4 - Reporting & Communication: Same Facts, Different Audience

- [ ] Meeting-minutes chain (parser -> AI analysis -> Word generator), wired into the app
- [ ] Executive status-report generator
- [ ] RACI matrix generator
- [ ] Audience/tone selector (executive vs. team)

## Phase 5 - Integration & Responsible Use: Where the Tool Meets Real Work

- [ ] Responsible Use section in the README
- [ ] Stretch: one external tool integration (Jira or Notion API)
- [ ] Capstone run: plain-language idea -> charter -> WBS -> risk register -> status report, all as real documents

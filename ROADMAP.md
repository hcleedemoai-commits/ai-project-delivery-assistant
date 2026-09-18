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

## Phase 4 - Reporting & Communication: Same Facts, Different Audience ✅

- [x] Meeting-minutes chain (parser -> AI analysis -> Word generator), wired into the app
- [x] Executive status-report generator
- [x] RACI matrix generator (AI assigns roles, Python checks the one-Accountable rule)
- [x] Audience/tone selector (executive vs. team) - same prompt template, different instructions block

## Phase 5 - Integration & Responsible Use: Where the Tool Meets Real Work

- [x] Responsible Use section in the README
      -> expanded beyond the original Phase 1 stub to cover the Phase 5
      integrations specifically: data pushed to Notion/Jira becomes a
      real third-party record (not just a local file), and why Meeting
      Action Items auto-push to Jira but Risk Register entries
      deliberately don't (see the integration note above) - also
      refreshed the rest of the README (Status, Project Structure,
      Quick Start) which had drifted since Phase 1
- [x] Stretch: one external tool integration (Jira or Notion API)
      -> ended up building both, after deciding what belongs in each:
      - Notion: Status Report data pushed as blocks onto a live,
        shareable page (same `data` dict the .docx generator already
        uses - one AI call, two destinations)
      - Jira: Meeting Minutes' Action Items, each turned into its own
        issue - chosen over the alternatives after evaluating them:
        Risk Register entries are still AI-drafted speculation until a
        person reviews them (pushing them to Jira automatically would
        pollute the backlog with tickets nobody decided to act on), and
        WBS tasks are already tracked in the project schedule (a second
        ticket would just duplicate it). Action items are different -
        someone already committed to them out loud in the meeting -
        which is exactly what an issue tracker is for.
- [x] Capstone run: plain-language idea -> charter -> WBS -> risk register -> status report, all as real documents
      -> ran end to end using a real-world idea (Singapore's IRAS GST
      InvoiceNow mandate, ERP-to-Peppol integration) instead of a
      generic placeholder, carried the same project description through
      all four features by hand (Charter -> WBS -> Risk Register ->
      Status Report don't auto-chain today - see the note this run
      surfaced, below), and verified along the way: the AI's own
      assumption about the compliance deadline was wrong in the first
      Charter draft and had to be corrected by supplying the real date;
      the Risk Register's likelihood/impact values correctly triggered
      `escalation.py`'s fixed rule on 5 of 8 risks
      Note for a future iteration: only WBS -> Timeline auto-carries
      data via `st.session_state` today. Charter -> WBS -> Risk Register
      -> Status Report do not - consider whether that's worth wiring up

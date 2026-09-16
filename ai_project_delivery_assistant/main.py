"""
AI Project Delivery Assistant - Phase 1
Proves the real Claude round trip works end to end: browser -> prompt -> Claude -> response.
"""

import sys
from pathlib import Path

# Make the project root importable no matter how Streamlit was launched
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os

import streamlit as st

from ai_project_delivery_assistant.config import Config
from ai_project_delivery_assistant.ai_engine.ai_factory import AIFactory
from ai_project_delivery_assistant.ai_engine.response_parser import AIResponseParser
from ai_project_delivery_assistant.prompts.charter_prompt import build_charter_prompt
from ai_project_delivery_assistant.generators.charter_generator import CharterGenerator
from ai_project_delivery_assistant.prompts.wbs_prompt import (
    build_wbs_phases_prompt,
    build_wbs_tasks_prompt,
)
from ai_project_delivery_assistant.generators.wbs_generator import WBSGenerator
from ai_project_delivery_assistant.prompts.timeline_prompt import build_timeline_prompt
from ai_project_delivery_assistant.generators.timeline_generator import TimelineGenerator
from ai_project_delivery_assistant.prompts.risk_prompt import build_risk_prompt
from ai_project_delivery_assistant.generators.risk_generator import RiskGenerator
from ai_project_delivery_assistant.prompts.decision_prompt import build_decision_prompt
from ai_project_delivery_assistant.generators.decision_generator import DecisionGenerator


st.set_page_config(page_title="AI Project Delivery Assistant", page_icon="🤖")


def main():
    st.title("🤖 AI Project Delivery Assistant")
    st.caption("Phase 1 — proving the real Claude round trip works, end to end.")

    try:
        Config.validate()
    except ValueError as e:
        st.error(str(e))
        st.stop()

    st.info(
        f"AI provider: **{Config.AI_PROVIDER}**  ·  "
        "change AI_PROVIDER in your .env to switch between claude / openrouter / mock"
    )

    tab_quick, tab_structured, tab_charter, tab_wbs, tab_timeline, tab_risk, tab_decision = st.tabs(
        [
            "Quick Prompt",
            "Structured BA Review",
            "Project Charter",
            "Work Breakdown Structure",
            "Milestones & Timeline",
            "Risk Register",
            "Decision Matrix",
        ]
    )

    # ---- Task: smallest possible loop - prompt in, raw text out ----
    with tab_quick:
        st.write("Send any prompt straight to the AI provider and see the raw response.")

        prompt = st.text_area(
            "Prompt",
            value="Explain what a Business Analyst does in one sentence.",
            height=100,
        )

        if st.button("Send", key="quick_send"):
            with st.spinner("Calling AI..."):
                ai = AIFactory.create()
                result = ai.generate(prompt)

            st.subheader("Response")
            st.write(result)

    # ---- Task: upgrade the prompt to demand structured JSON, then parse it ----
    with tab_structured:
        st.write(
            "Paste rough project requirement notes below. The AI acts as a "
            "Senior Business Analyst and returns structured JSON: missing "
            "information, risks, and clarification questions."
        )

        requirement_text = st.text_area(
            "Requirement notes",
            value=(
                "Project: Customer Portal\n"
                "We want customers to log in and view their order history."
            ),
            height=150,
        )

        if st.button("Analyze", key="structured_send"):
            structured_prompt = f"""
You are a Senior Business Analyst reviewing a software requirement.

Requirement notes:
{requirement_text}

Identify:
1. Missing information
2. Project risks
3. Clarification questions

Return your answer as JSON only, with exactly these keys:
missing_information (list of strings), risks (list of strings), questions (list of strings).
""".strip()

            with st.spinner("Analyzing..."):
                ai = AIFactory.create()
                raw_result = ai.generate(structured_prompt)
                result = AIResponseParser().parse(raw_result)

            st.subheader("Structured result")

            if "error" in result:
                st.warning(result["error"])
                st.text(result.get("raw_response", ""))
            else:
                st.json(result)

    # ---- Phase 2: plain-language idea -> structured charter -> Word doc ----
    with tab_charter:
        st.write(
            "Describe a project idea in a sentence or two. The AI acts as a "
            "Senior Project Manager and drafts a project charter: objectives, "
            "scope, constraints, assumptions, and stakeholders."
        )

        idea_text = st.text_area(
            "Project idea",
            value=(
                "We want to build a customer portal so our clients can log in, "
                "see their order history, and download invoices themselves "
                "instead of emailing support."
            ),
            height=120,
        )

        if st.button("Generate Charter", key="charter_send"):
            prompt = build_charter_prompt(idea_text)

            with st.spinner("Drafting charter..."):
                ai = AIFactory.create()
                raw_result = ai.generate(prompt)
                charter_data = AIResponseParser().parse(raw_result)

            if "error" in charter_data:
                st.warning(charter_data["error"])
                st.text(charter_data.get("raw_response", ""))
            else:
                st.subheader("Charter preview")
                st.json(charter_data)

                os.makedirs(Config.REPORTS_DIR, exist_ok=True)
                output_path = os.path.join(Config.REPORTS_DIR, "Project_Charter.docx")

                CharterGenerator().generate(charter_data, output_path)

                with open(output_path, "rb") as f:
                    st.download_button(
                        "Download Project_Charter.docx",
                        data=f.read(),
                        file_name="Project_Charter.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )

    # ---- Phase 2: WBS via iterative prompting (phases first, then tasks per phase) ----
    with tab_wbs:
        st.write(
            "Describe the project. The AI first drafts the major phases, then "
            "drills into detailed tasks one phase at a time - two prompting "
            "steps instead of one, for a deeper breakdown."
        )

        wbs_project_name = st.text_input("Project name", value="Customer Portal")
        wbs_idea_text = st.text_area(
            "Project idea",
            value=(
                "Build a customer portal so clients can log in, view order "
                "history, and download invoices themselves."
            ),
            height=120,
            key="wbs_idea",
        )

        if st.button("Generate WBS", key="wbs_send"):
            ai = AIFactory.create()
            parser = AIResponseParser()

            # Step 1: major phases only
            with st.spinner("Step 1/2: drafting major phases..."):
                phases_raw = ai.generate(build_wbs_phases_prompt(wbs_idea_text))
                phases_result = parser.parse(phases_raw)

            if "error" in phases_result or "phases" not in phases_result:
                st.warning("Could not get a valid phase list from the AI.")
                st.text(phases_result.get("raw_response", phases_raw))
            else:
                phases = phases_result["phases"]
                st.success(f"Got {len(phases)} phases. Now drafting tasks for each one...")

                progress = st.progress(0.0)
                wbs_data = {"project_name": wbs_project_name, "phases": []}

                # Step 2: tasks for each phase, one AI call per phase
                for i, phase in enumerate(phases):
                    phase_name = phase.get("phase_name", f"Phase {i + 1}")
                    phase_goal = phase.get("phase_goal", "")

                    tasks_raw = ai.generate(
                        build_wbs_tasks_prompt(wbs_idea_text, phase_name, phase_goal)
                    )
                    tasks_result = parser.parse(tasks_raw)
                    tasks = tasks_result.get("tasks", [])  # [] if that call failed - don't abort the whole WBS

                    wbs_data["phases"].append(
                        {"phase_name": phase_name, "phase_goal": phase_goal, "tasks": tasks}
                    )
                    progress.progress((i + 1) / len(phases))

                st.subheader("WBS preview")
                st.json(wbs_data)

                # remembered across tabs/reruns so the Timeline tab can build on it
                # without asking the user to redo the whole breakdown
                st.session_state["wbs_data"] = wbs_data

                os.makedirs(Config.REPORTS_DIR, exist_ok=True)
                wbs_output_path = os.path.join(Config.REPORTS_DIR, "Work_Breakdown_Structure.docx")

                WBSGenerator().generate(wbs_data, wbs_output_path)

                with open(wbs_output_path, "rb") as f:
                    st.download_button(
                        "Download Work_Breakdown_Structure.docx",
                        data=f.read(),
                        file_name="Work_Breakdown_Structure.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="wbs_download",
                    )

    # ---- Phase 2: Milestones & Timeline - builds on the WBS, doesn't restart from scratch ----
    with tab_timeline:
        st.write(
            "Milestones and sequencing are proposed from the phases and tasks "
            "you already generated in the Work Breakdown Structure tab."
        )

        wbs_data = st.session_state.get("wbs_data")

        if not wbs_data:
            st.info("Generate a WBS first in the previous tab - milestones are built from your phases.")
        else:
            st.write(f"Using the WBS for **{wbs_data.get('project_name', 'Untitled Project')}** "
                      f"({len(wbs_data.get('phases', []))} phases).")

            if st.button("Generate Milestones & Timeline", key="timeline_send"):
                prompt = build_timeline_prompt(
                    wbs_data.get("project_name", "Untitled Project"),
                    wbs_data.get("phases", []),
                )

                with st.spinner("Proposing milestones and sequencing..."):
                    ai = AIFactory.create()
                    raw_result = ai.generate(prompt)
                    timeline_data = AIResponseParser().parse(raw_result)

                if "error" in timeline_data:
                    st.warning(timeline_data["error"])
                    st.text(timeline_data.get("raw_response", ""))
                else:
                    timeline_data["project_name"] = wbs_data.get("project_name", "Untitled Project")

                    st.subheader("Timeline preview")
                    st.json(timeline_data)

                    os.makedirs(Config.REPORTS_DIR, exist_ok=True)
                    timeline_output_path = os.path.join(
                        Config.REPORTS_DIR, "Milestones_and_Timeline.docx"
                    )

                    TimelineGenerator().generate(timeline_data, timeline_output_path)

                    with open(timeline_output_path, "rb") as f:
                        st.download_button(
                            "Download Milestones_and_Timeline.docx",
                            data=f.read(),
                            file_name="Milestones_and_Timeline.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="timeline_download",
                        )


    # ---- Phase 3: Risk Register - identify risks, apply a fixed escalation rule ----
    with tab_risk:
        st.write(
            "Describe a project idea. The AI acts as a Senior Risk Manager "
            "and identifies delivery risks with likelihood, impact, "
            "mitigation, and an accountable owner role. Which risks get "
            "escalated is decided by a fixed rule in this app, not by the "
            "AI, so the answer is consistent every time."
        )

        risk_idea_text = st.text_area(
            "Project idea",
            value=(
                "We want to build a customer portal so clients can log in, "
                "view order history, and download invoices themselves "
                "instead of emailing support."
            ),
            height=120,
            key="risk_idea",
        )

        if st.button("Generate Risk Register", key="risk_send"):
            prompt = build_risk_prompt(risk_idea_text)

            with st.spinner("Identifying risks..."):
                ai = AIFactory.create()
                raw_result = ai.generate(prompt)
                risk_data = AIResponseParser().parse(raw_result)

            if "error" in risk_data:
                st.warning(risk_data["error"])
                st.text(risk_data.get("raw_response", ""))
            else:
                st.subheader("Risk Register preview")
                st.json(risk_data)

                os.makedirs(Config.REPORTS_DIR, exist_ok=True)
                risk_output_path = os.path.join(Config.REPORTS_DIR, "Risk_Register.docx")

                RiskGenerator().generate(risk_data, risk_output_path)

                with open(risk_output_path, "rb") as f:
                    st.download_button(
                        "Download Risk_Register.docx",
                        data=f.read(),
                        file_name="Risk_Register.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="risk_download",
                    )


    # ---- Phase 3: Decision Matrix - AI scores options, Python computes the weighted result ----
    with tab_decision:
        st.write(
            "Describe a decision you're weighing. The AI acts as a Senior "
            "Business Analyst and proposes realistic options, weighted "
            "criteria, and a score for each option against each criterion. "
            "The weighted total and recommendation are then computed by "
            "this app, not by the AI, so the same inputs always produce "
            "the same recommendation."
        )

        decision_idea_text = st.text_area(
            "Decision to analyze",
            value=(
                "We need to decide how to build the customer portal's "
                "authentication: build our own login system, use a "
                "third-party identity provider, or extend our existing "
                "internal SSO."
            ),
            height=120,
            key="decision_idea",
        )

        if st.button("Generate Decision Matrix", key="decision_send"):
            prompt = build_decision_prompt(decision_idea_text)

            with st.spinner("Scoring options..."):
                ai = AIFactory.create()
                raw_result = ai.generate(prompt)
                decision_data = AIResponseParser().parse(raw_result)

            if "error" in decision_data:
                st.warning(decision_data["error"])
                st.text(decision_data.get("raw_response", ""))
            else:
                st.subheader("Decision Matrix preview")
                st.json(decision_data)

                os.makedirs(Config.REPORTS_DIR, exist_ok=True)
                decision_output_path = os.path.join(Config.REPORTS_DIR, "Decision_Matrix.docx")

                DecisionGenerator().generate(decision_data, decision_output_path)

                with open(decision_output_path, "rb") as f:
                    st.download_button(
                        "Download Decision_Matrix.docx",
                        data=f.read(),
                        file_name="Decision_Matrix.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="decision_download",
                    )


if __name__ == "__main__":
    main()

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

import streamlit as st

from ai_project_delivery_assistant.config import Config
from ai_project_delivery_assistant.ai_engine.ai_factory import AIFactory
from ai_project_delivery_assistant.ai_engine.response_parser import AIResponseParser


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

    tab_quick, tab_structured = st.tabs(["Quick Prompt", "Structured BA Review"])

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


if __name__ == "__main__":
    main()

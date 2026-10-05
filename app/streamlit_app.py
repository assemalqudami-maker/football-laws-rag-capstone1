"""Streamlit interface for the Football Laws Referee RAG."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from football_rag.generation import FootballLawsRAG  # noqa: E402


st.set_page_config(
    page_title="Football Laws Referee RAG",
    page_icon="⚽",
    layout="centered",
)


def login() -> bool:
    expected_user = os.getenv("APP_USERNAME")
    expected_password = os.getenv("APP_PASSWORD")

    if not expected_user or not expected_password:
        st.error(
            "Authentication is not configured. Set APP_USERNAME and APP_PASSWORD "
            "as deployment secrets."
        )
        return False

    if st.session_state.get("authenticated"):
        return True

    st.title("⚽ Football Laws Referee RAG")
    st.caption("Sign in to access the referee-law assistant.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

    if submitted:
        if username == expected_user and password == expected_password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid username or password.")
    return False


@st.cache_resource(show_spinner="Loading retrieval models and index...")
def get_rag() -> FootballLawsRAG:
    return FootballLawsRAG()


if not login():
    st.stop()

with st.sidebar:
    st.markdown("### About")
    st.write(
        "Answers are grounded in the official IFAB corpus indexed for this project. "
        "This is an educational tool, not an official match ruling."
    )
    st.markdown("**Retrieval:** Dense + BM25 + RRF + Cohere Rerank v4.0 Pro")
    st.markdown("**Generator:** Cohere Command A")
    st.markdown("**Language:** English")
    if st.button("Sign out"):
        st.session_state.authenticated = False
        st.rerun()

st.title("⚽ Football Laws Referee RAG")
st.caption(
    "Ask about the Laws of the Game, refereeing, disciplinary sanctions, "
    "restarts, offside, VAR, and related IFAB protocols."
)

if "history" not in st.session_state:
    st.session_state.history = []

examples = [
    "Is being in an offside position itself an offence?",
    "When can the referee apply advantage?",
    "What are the four VAR review categories?",
    "Can a goal be scored directly from a throw-in?",
]
example = st.selectbox("Example questions", [""] + examples)

question = st.text_area(
    "Your question",
    value=example,
    height=100,
    placeholder="Example: When is a defender sent off for DOGSO?",
)

if st.button("Ask the referee assistant", type="primary", use_container_width=True):
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        start = time.perf_counter()
        try:
            result = get_rag().answer(question)
            elapsed = time.perf_counter() - start

            st.markdown("### Answer")
            st.markdown(result.answer)
            st.caption(f"Response time: {elapsed:.2f} s")

            st.markdown("### Retrieved evidence")
            for i, source in enumerate(result.sources, start=1):
                where = source.get("section") or "Relevant section"
                if source.get("page") not in (None, -1):
                    where = f"{where} — page {source['page']}"
                with st.expander(f"[{i}] {source['title']} — {where}"):
                    st.write(source["content"])
                    st.link_button("Open official source", source["url"])

            st.session_state.history.insert(
                0, {"question": question, "answer": result.answer}
            )
            st.session_state.history = st.session_state.history[:5]
        except Exception as exc:
            st.error(f"Unable to answer: {exc}")

if st.session_state.history:
    st.divider()
    st.markdown("### Recent questions")
    for item in st.session_state.history:
        with st.expander(item["question"]):
            st.write(item["answer"])

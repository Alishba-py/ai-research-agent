"""
AI Research Agent
Free stack: Groq (LLM) + Tavily (search) + Streamlit (UI)

How it works:
1. User enters a research topic/question
2. Agent searches the web via Tavily (returns content-rich results, not just links)
3. Groq LLM reads the results and synthesizes a structured research report
4. Report is shown with clickable sources
"""

import streamlit as st
from groq import Groq
from tavily import TavilyClient
import os
import re

# ---------- CONFIG ----------
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Read API keys from Streamlit secrets (for deployed app) or env vars (for local run)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY", os.environ.get("TAVILY_API_KEY", ""))

GROQ_MODEL = "llama-3.3-70b-versatile"  # free tier, strong reasoning, good for synthesis


# ---------- DARK THEME / CUSTOM STYLING ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg: #08090b;
    --surface: #121317;
    --surface-hi: #1a1c22;
    --border: #24262e;
    --accent: #7c5cff;
    --accent-2: #22d3ee;
    --text: #e8e8ec;
    --text-dim: #9a9ba5;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 20% 0%, #14101f 0%, var(--bg) 45%);
    color: var(--text);
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}

/* Hero header */
.hero {
    padding: 2.2rem 0 1.4rem 0;
    text-align: center;
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #ffffff 0%, var(--accent) 55%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.hero p {
    color: var(--text-dim);
    font-size: 0.98rem;
    margin: 0;
}
.pill-row {
    display: flex;
    justify-content: center;
    gap: 0.6rem;
    margin-top: 1.1rem;
    flex-wrap: wrap;
}
.pill {
    background: rgba(124, 92, 255, 0.1);
    border: 1px solid rgba(124, 92, 255, 0.3);
    color: #cfcaff;
    font-size: 0.78rem;
    font-weight: 500;
    padding: 0.32rem 0.85rem;
    border-radius: 999px;
}

/* Input styling — target BaseWeb's wrapping container, not just the raw <input> */
div[data-testid="stTextInput"] > div > div {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
div[data-testid="stTextInput"] > div > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124, 92, 255, 0.18) !important;
}
div[data-testid="stTextInput"] input {
    background-color: transparent !important;
    border: none !important;
    color: #ffffff !important;
    padding: 0.9rem 1.1rem !important;
    font-size: 0.98rem !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #6a6b75 !important;
    opacity: 1 !important;
}
div[data-testid="stTextInput"] label {
    color: var(--text-dim) !important;
    font-size: 0.85rem !important;
}
div[data-testid="stTextInput"] svg {
    display: none !important;
}

/* Selectbox */
div[data-testid="stSelectbox"] > div > div {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}
div[data-testid="stSelectbox"] > div > div:hover {
    border-color: #3d3f4a !important;
}
div[data-testid="stSelectbox"] label {
    color: var(--text-dim) !important;
    font-size: 0.85rem !important;
}
div[data-testid="stSelectbox"] svg {
    fill: var(--text-dim) !important;
}

/* Form card — wraps input + selectbox + button together */
.st-key-form_container {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    padding: 1.8rem 2rem 1.6rem 2rem !important;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3) !important;
}

/* Primary button */
.stButton > button {
    background: linear-gradient(90deg, var(--accent) 0%, #6845ff 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 20px rgba(124, 92, 255, 0.35) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    width: 100% !important;
    margin-top: 0.4rem !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 24px rgba(124, 92, 255, 0.5) !important;
}

/* Report card — targets Streamlit's real bordered container (key="report_container") */
.st-key-report_container {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.6rem 2rem !important;
    margin-top: 1.5rem !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.35) !important;
}
.st-key-report_container h1,
.st-key-report_container h2,
.st-key-report_container h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #ffffff !important;
}
.st-key-report_container h2 {
    font-size: 1.25rem !important;
    margin-top: 1.6rem !important;
    border-left: 3px solid var(--accent) !important;
    padding-left: 0.6rem !important;
}
.st-key-report_container p,
.st-key-report_container li {
    color: #cfd0d8 !important;
    line-height: 1.7 !important;
    font-size: 0.97rem !important;
}
.st-key-report_container strong {
    color: var(--accent-2) !important;
}

/* Sources container — same bordered-container technique */
.st-key-sources_container {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.4rem 1.8rem !important;
    margin-top: 1.2rem !important;
}

/* Individual source rows inside sources container */
.source-card {
    background: #1e2029 !important;
    border: 1px solid #34363f !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.1rem !important;
    margin-bottom: 0.55rem !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.8rem !important;
    transition: border-color 0.15s ease, background 0.15s ease;
}
.source-card:hover {
    border-color: var(--accent) !important;
    background: #23262f !important;
}
.source-num {
    background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
    color: #08090b !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    width: 24px !important;
    height: 24px !important;
    min-width: 24px !important;
    border-radius: 6px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-shrink: 0 !important;
}
.source-card a {
    color: #f0f0f4 !important;
    text-decoration: none !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    line-height: 1.4 !important;
}
.source-card a:visited {
    color: #f0f0f4 !important;
}
.source-card a:hover {
    color: var(--accent-2) !important;
}

.sources-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    color: #ffffff !important;
    margin: 0 0 0.4rem 0 !important;
}

/* Footer */
.footer-note {
    text-align: center;
    color: #55565f;
    font-size: 0.8rem;
    margin-top: 2.5rem;
    padding-bottom: 1rem;
}

/* Spinner text */
.stSpinner > div {
    color: var(--accent-2) !important;
}
</style>
""", unsafe_allow_html=True)


# ---------- AGENT LOGIC ----------
def web_search(query: str, max_results: int = 6):
    """Search the web using Tavily and return content-rich results."""
    client = TavilyClient(api_key=TAVILY_API_KEY)
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
    )
    return response.get("results", [])


def build_context(results):
    """Turn search results into a numbered source block for the LLM prompt."""
    blocks = []
    for i, r in enumerate(results, start=1):
        title = r.get("title", "Untitled")
        url = r.get("url", "")
        content = r.get("content", "")[:1500]  # keep prompt size reasonable
        blocks.append(f"[Source {i}] {title}\nURL: {url}\nContent: {content}\n")
    return "\n".join(blocks)


def synthesize_report(query: str, results):
    """Send search results to Groq LLM and get a structured research report back."""
    context = build_context(results)

    system_prompt = (
        "You are a careful research analyst. You are given a research question and a set "
        "of numbered web sources with excerpts. Write a clear, well-structured research "
        "report that directly answers the question using ONLY the information in the "
        "sources. Cite sources inline like [1], [2] matching the source numbers. "
        "If sources disagree, point that out. If information is missing, say so honestly "
        "instead of guessing. Use markdown headings and bullet points where helpful."
    )

    user_prompt = f"Research question: {query}\n\nSources:\n{context}\n\nWrite the report now."

    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=2000,
    )
    return completion.choices[0].message.content


def linkify_citations(text: str, num_sources: int) -> str:
    """Turn [1] [2] style citations into styled superscript-like badges (markdown-safe)."""
    def repl(match):
        n = match.group(1)
        return f"**`[{n}]`**"
    return re.sub(r"\[(\d+)\]", repl, text)


# ---------- UI ----------
st.markdown("""
<div class="hero">
    <h1>🔎 AI Research Agent</h1>
    <p>Enter a topic → agent searches the live web → synthesizes a sourced report</p>
    <div class="pill-row">
        <span class="pill">⚡ Groq LLM</span>
        <span class="pill">🌐 Tavily Search</span>
        <span class="pill">🆓 100% Free</span>
    </div>
</div>
""", unsafe_allow_html=True)

if not GROQ_API_KEY or not TAVILY_API_KEY:
    st.warning(
        "API keys not found. Add GROQ_API_KEY and TAVILY_API_KEY in Streamlit "
        "secrets (deployed) or as environment variables (local run). See README.md."
    )

with st.container(border=False, key="form_container"):
    query = st.text_input(
        "Research topic or question",
        placeholder="e.g. What are the latest advances in small language models in 2026?",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        num_sources = st.selectbox("Sources", [4, 6, 8], index=1)
    run = st.button("Run Research", type="primary", use_container_width=True)


if run:
    if not query.strip():
        st.error("Please enter a research topic first.")
    elif not GROQ_API_KEY or not TAVILY_API_KEY:
        st.error("Missing API keys — cannot run without them.")
    else:
        with st.spinner("Searching the web..."):
            try:
                results = web_search(query, max_results=num_sources)
            except Exception as e:
                st.error(f"Search failed: {e}")
                results = []

        if not results:
            st.warning("No results found. Try rephrasing your query.")
        else:
            with st.spinner("Synthesizing report..."):
                try:
                    report = synthesize_report(query, results)
                except Exception as e:
                    st.error(f"LLM synthesis failed: {e}")
                    report = None

            if report:
                styled_report = linkify_citations(report, len(results))
                with st.container(border=True, key="report_container"):
                    st.markdown(styled_report)

                with st.container(border=True, key="sources_container"):
                    st.markdown('<div class="sources-title">📚 Sources</div>', unsafe_allow_html=True)
                    for i, r in enumerate(results, start=1):
                        title = r.get("title", "Untitled")
                        url = r.get("url", "")
                        st.markdown(
                            f'<div class="source-card">'
                            f'<div class="source-num">{i}</div>'
                            f'<a href="{url}" target="_blank">{title}</a>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

st.markdown(
    '<div class="footer-note">Built with Streamlit + Groq (LLM) + Tavily (search) — all free-tier services.</div>',
    unsafe_allow_html=True,
)
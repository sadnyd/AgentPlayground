"""
app.py
======

Streamlit entrypoint for the LangChain Agent Playground.

This is a thin orchestrator — all logic lives in the ui/ package:
 - ui.logging_setup   -> logging config
 - ui.discovery       -> dynamic component scanning
 - ui.model_params    -> per-model parameter schemas & widgets
 - ui.agent_factory   -> cached agent construction
 - ui.streaming       -> streaming execution loop & renderers
 - ui.sidebar         -> sidebar configuration panel
 - ui.chat            -> chat history & input handling
"""

import streamlit as st
from langchain_core.utils.uuid import uuid7
from phoenix.otel import register
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------
# Phoenix OTEL tracing
# ------------------------------------------------------------------



tracer_provider = register(
    project_name="first-langchain-agent",
    auto_instrument=True,
    set_global_tracer_provider=False,
)

# ------------------------------------------------------------------
# Ensure logging is initialised early
# ------------------------------------------------------------------

import ui.logging_setup  # noqa: F401 (side-effect: configures logger + creates logs/)

from ui.chat import handle_user_input, render_chat_history
from ui.discovery import discover
from ui.sidebar import render_sidebar

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------

st.set_page_config(
    page_title="Agent Playground",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Agent Playground")

# ------------------------------------------------------------------
# Discover workspace components
# ------------------------------------------------------------------

registry = discover()

# Show any discovery errors
if registry.get("errors"):
    with st.expander("⚠️ Component load warnings", expanded=False):
        for err in registry["errors"]:
            st.warning(err)

# ------------------------------------------------------------------
# Session state initialisation
# ------------------------------------------------------------------

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid7())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------------------------------------------------------
# Sidebar -> config dict
# ------------------------------------------------------------------

config = render_sidebar(registry)

# ------------------------------------------------------------------
# Chat panel
# ------------------------------------------------------------------

render_chat_history()
handle_user_input(registry, config)


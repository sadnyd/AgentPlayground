from typing import Any

import streamlit as st

from ui.discovery import _discover_cached as discover_cached


@st.cache_resource(show_spinner=False)
def build_agent(
    model_key: str,
    tool_keys: tuple[str, ...],
    middleware_keys: tuple[str, ...],
    checkpointer_key: str,
    agent_name: str,
    system_prompt: str,
    cache_bust: int,
) -> Any:
    """
    Build and cache the agent.

    Cache is keyed on every config value.
    """

    from langchain.agents import create_agent

    reg = discover_cached(cache_bust)

    model = reg["clients"][model_key]

    tools = [
        reg["tools"][k]
        for k in tool_keys
    ]

    mw = [
        reg["middleware"][k]
        for k in middleware_keys
    ]

    checkpointer = reg["checkpointers"][checkpointer_key]

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        middleware=mw,
        name=agent_name or "StreamlitAgent",
        checkpointer=checkpointer,
    )